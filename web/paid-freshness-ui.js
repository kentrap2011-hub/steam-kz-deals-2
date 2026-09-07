(function (root) {
  function paidFreshnessTimestamp(payload) {
    const freshness = payload && payload.paid_list_freshness;
    if (freshness && freshness.status === 'published' && freshness.source_mailing_updated_at_utc) {
      return freshness.source_mailing_updated_at_utc;
    }
    return payload && payload.commercial_source_mailing_updated_at_utc
      ? payload.commercial_source_mailing_updated_at_utc
      : null;
  }

  function paidFreshnessLabel(payload, locale = 'ru-RU') {
    const value = paidFreshnessTimestamp(payload);
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    const rendered = new Intl.DateTimeFormat(locale, {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
    return `Скидки: обновлено ${rendered}`;
  }

  async function loadPaidFreshnessPayload() {
    const response = await fetch('data/current.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`paid freshness payload HTTP ${response.status}`);
    return response.json();
  }

  async function installPaidFreshnessUi() {
    const element = document.getElementById('freshness');
    if (!element) return;

    let payload = null;
    try {
      payload = await loadPaidFreshnessPayload();
    } catch (error) {
      console.warn('Paid freshness indicator unavailable', error);
      return;
    }

    const label = paidFreshnessLabel(payload);
    const timestamp = paidFreshnessTimestamp(payload);
    if (!label || !timestamp) return;

    const apply = () => {
      if (element.textContent !== label) element.textContent = label;
      element.title = `Коммерческие данные основного списка: ${timestamp}`;
      element.dataset.freshnessDomain = 'paid-list';
    };

    const observer = new MutationObserver(apply);
    observer.observe(element, { childList: true, characterData: true, subtree: true });
    apply();
  }

  const api = { paidFreshnessTimestamp, paidFreshnessLabel };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.PaidFreshnessUi = api;

  if (typeof document !== 'undefined' && typeof MutationObserver !== 'undefined') {
    installPaidFreshnessUi();
  }
})(typeof window !== 'undefined' ? window : globalThis);

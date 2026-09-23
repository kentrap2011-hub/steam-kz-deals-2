import ingest_progressive_pass1


def assert_rejected(work):
    try:
        ingest_progressive_pass1.validate_activation_flags(work)
    except SystemExit as exc:
        assert str(exc) == 'Progressive PASS 1 work activation flags are invalid'
    else:
        raise AssertionError(f'incompatible activation flags were accepted: {work!r}')


def main():
    ingest_progressive_pass1.validate_activation_flags({
        'pass1_active': True,
        'pass2_active': True,
    })

    for work in (
        {'pass1_active': True, 'pass2_active': False},
        {'pass1_active': False, 'pass2_active': True},
        {'pass1_active': False, 'pass2_active': False},
        {'pass1_active': True},
        {'pass2_active': True},
        {},
    ):
        assert_rejected(work)

    print('progressive PASS 1 ingest activation regression: ok')


if __name__ == '__main__':
    main()

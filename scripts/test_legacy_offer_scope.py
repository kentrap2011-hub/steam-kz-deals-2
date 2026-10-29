import unittest
from legacy_offer_scope import put_feed, current_includes, assert_family_inputs, validate_metadata_identity

def fixture():
    feed={}
    put_feed(feed,{'key':'App_2','appid':'2','title':'Live','final_kzt':100})
    taste={'App_1':['1','f','INCLUDE','strong','ok'],'App_2':['2','f','INCLUDE','strong','ok']}
    meta={'mailing_tree_sha':'mail','taste_index_blob_sha':'taste','entry_count':1,'required_include_count':1,
          'out_of_current_feed_keys':['App_1'],'entries':{'App_2':{'key':'App_2','entity_kind':'app','steam_id':'2','app_type':'game'}}}
    elig={'status':'complete','complete_coverage':True,'unresolved_count':0,
          'bindings':{'policy_blob_sha':'policy','mailing_tree_sha':'mail','content_metadata_blob_sha':'meta','taste_index_blob_sha':'taste'},
          'eligible':[{'key':'App_2','appid':'2'}],'excluded':[],'eligible_count':1,'excluded_count':0,
          'classified_count':1,'input_taste_include_count':1,'historical_taste_include_count':2,
          'out_of_current_feed_keys':['App_1'],'out_of_current_feed_count':1}
    return feed,taste,meta,elig

class CurrentOfferScopeRegression(unittest.TestCase):
    def check(self,feed,meta,elig,mail='mail',taste_index='taste'):
        return assert_family_inputs(elig,meta,feed,policy_sha='policy',mailing_sha=mail,metadata_sha='meta',taste_index_sha=taste_index)
    def test_inactive_historical_cache_entry_not_current_offer(self):
        feed,taste,meta,elig=fixture()
        self.assertEqual(current_includes(taste,feed),(['App_2'],['App_1']))
        self.assertEqual(self.check(feed,meta,elig),{'App_2'})
    def test_missing_eligible_feed_key_fails_closed(self):
        feed,_,meta,elig=fixture()
        elig['eligible'].append({'key':'App_1','appid':'1'})
        elig['eligible_count']=elig['classified_count']=elig['input_taste_include_count']=2
        meta['entries']['App_1']={'steam_id':'1'}
        meta['entry_count']=meta['required_include_count']=2
        with self.assertRaisesRegex(ValueError,'missing eligible keys'): self.check(feed,meta,elig)
    def test_stale_source_bindings_fail_closed(self):
        feed,_,meta,elig=fixture()
        with self.assertRaisesRegex(ValueError,'Stale eligibility'): self.check(feed,meta,elig,mail='other')
        meta['taste_index_blob_sha']='other'
        with self.assertRaisesRegex(ValueError,'Stale metadata'): self.check(feed,meta,elig)
    def test_reused_cached_metadata_identity_rejected_before_consumption(self):
        feed,_,meta,elig=fixture()
        cached=meta['entries']['App_2']
        for field,corruption in [('key','App_999'),('entity_kind','sub'),('steam_id','999')]:
            with self.subTest(field=field):
                original=cached[field]
                cached[field]=corruption
                with self.assertRaisesRegex(ValueError,'Metadata identity mismatch'):
                    validate_metadata_identity('App_2',cached,feed['App_2'])
                with self.assertRaisesRegex(ValueError,'Metadata identity mismatch'):
                    self.check(feed,meta,elig)
                cached[field]=original

    def test_sub_metadata_identity_is_package_id_not_representative_appid(self):
        feed,taste,meta,elig=fixture()
        put_feed(feed,{'key':'Sub_456','appid':'2','title':'Live package','final_kzt':90})
        taste['Sub_456']=['2','f','INCLUDE','strong','ok']
        meta['entries']['Sub_456']={'key':'Sub_456','entity_kind':'sub','steam_id':'456',
                                     'package_apps':[{'appid':'2'}]}
        meta['entry_count']=meta['required_include_count']=2
        elig['eligible'].append({'key':'Sub_456','appid':'2'})
        elig['eligible_count']=elig['classified_count']=elig['input_taste_include_count']=2
        elig['historical_taste_include_count']=3
        self.assertEqual(current_includes(taste,feed),(['App_2','Sub_456'],['App_1']))
        self.assertEqual(self.check(feed,meta,elig),{'App_2','Sub_456'})
        meta['entries']['Sub_456']['steam_id']='2'
        with self.assertRaisesRegex(ValueError,'Metadata identity mismatch'):
            self.check(feed,meta,elig)

    def test_both_persisted_taste_bindings_stale_against_head(self):
        feed,_,meta,elig=fixture()
        meta['taste_index_blob_sha']='old_A'
        elig['bindings']['taste_index_blob_sha']='old_A'
        with self.assertRaisesRegex(ValueError,'Stale current taste index'):
            self.check(feed,meta,elig,taste_index='new_B')

    def test_wrong_identity_and_duplicate_offer(self):
        feed,taste,_,_=fixture()
        taste['App_2'][0]='999'
        with self.assertRaisesRegex(ValueError,'AppID mismatch'): current_includes(taste,feed)
        with self.assertRaisesRegex(ValueError,'Duplicate'): put_feed(feed,{'key':'App_2','appid':'2'})
    def test_missing_reconciliation_receipt_rejected(self):
        feed,_,meta,elig=fixture()
        elig['out_of_current_feed_keys']=[]
        with self.assertRaisesRegex(ValueError,'reconciliation'): self.check(feed,meta,elig)

if __name__=='__main__': unittest.main()

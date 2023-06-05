import httpx
import selectolax
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import creds
from dataclasses import dataclass
import json


@dataclass
class AmbossScraper:
    base_url: str = 'https://www.amboss.com/de'

    def fetch(self, url):
        with httpx.Client() as client:
            response = client.get(url)
        return response

    def webdriversetup(self):
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        ff_opt = Options()
        # ff_opt.add_argument('-headless')
        ff_opt.add_argument('--no-sandbox')
        ff_opt.set_preference("general.useragent.override", useragent)
        ff_opt.page_load_strategy = 'eager'
        driver = WebDriver(options=ff_opt)
        return driver

    def get_cookies(self, driver):
        login_url = 'https://next.amboss.com/de/login'
        driver.get(login_url)
        driver.fullscreen_window()
        wait = WebDriverWait(driver, 20)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="E-Mail"]'))).send_keys(
            creds.email + Keys.TAB + creds.password + Keys.RETURN)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-e2e-test-id="ÜbersichtPage"]')))
        cookies = driver.get_cookies()
        driver.close()
        return cookies

    def scrape(self, article_url, cookies):
        param = article_url.split("/")
        course_id = param[5]
        eid = param[6]
        article_id = param[-1]
        payload = [{"operationName":"currentUserCourseBundles","variables":{"courseEid": course_id},"query":"query currentUserCourseBundles($courseEid: ID!) {\n  currentUserCourseBundles(courseEid: $courseEid) {\n    bundle {\n      eid\n      __typename\n    }\n    __typename\n  }\n}\n"},{"operationName":"currentUserCourseBundles","variables":{"eids":[eid]},"query":"query currentUserCourseBundles($eids: [ID!]!) {\n  currentUserBundles(eids: $eids) {\n    bundle {\n      eid\n      title\n      subtitle\n      articleEids\n      isCertified\n      targets {\n        eid\n        articleEid\n        articleTitle\n        anchorEid\n        anchorTitle\n        __typename\n      }\n      sessionTemplate {\n        eid\n        defaultMode\n        questionCount\n        availableQuestionCount\n        title\n        __typename\n      }\n      course {\n        eid\n        category\n        certificateInformation {\n          certificateType\n          percentToPass\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    userBundleDestinations {\n      status\n      bundleDestination {\n        eid\n        __typename\n      }\n      __typename\n    }\n    accessedAt\n    sessionEid\n    __typename\n  }\n}\n"},{"operationName":"articleQuestionResultsQuery","variables":{"eids":[article_id]},"query":"query articleQuestionResultsQuery($eids: [ID!]!) {\n  currentUserArticles(eids: $eids) {\n    article {\n      eid\n      __typename\n    }\n    questionResults {\n      sessionEid\n      questionEid\n      isAnswerCorrect\n      __typename\n    }\n    __typename\n  }\n}\n"},{"operationName":"userParticlesQuery","variables":{"eids":[article_id]},"query":"query userParticlesQuery($eids: [ID!]!) {\n  currentUserArticles(eids: $eids) {\n    article {\n      eid\n      __typename\n    }\n    userParticles {\n      particleEid\n      extension {\n        text\n        eid\n        ownerName\n        __typename\n      }\n      sharedExtensions {\n        text\n        eid\n        ownerName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"},{"operationName":"articleQuery","variables":{"eids":[article_id]},"query":"query articleQuery($eids: [ID!]!) {\n  currentUserArticles(eids: $eids) {\n    editorialLink {\n      ... on EditorialUrl {\n        url\n        __typename\n      }\n      ... on ForbiddenLink {\n        isForbidden\n        __typename\n      }\n      __typename\n    }\n    studyQuestionProgress {\n      studyObjectiveLabel\n      totalQuestions\n      __typename\n    }\n    article {\n      ...articleFullFragment\n      __typename\n    }\n    isLearned\n    __typename\n  }\n  maxQuestionsWithObjective: questionSessionCustomSize(\n    criteria: {learningCard: $eids, onlyStudyObjectiveRelated: true}\n  )\n  maxQuestionWithoutObjective: questionSessionCustomSize(\n    criteria: {learningCard: $eids}\n  )\n}\n\nfragment articleFullFragment on Article {\n  __typename\n  eid\n  title\n  synonyms\n  abstract\n  knowledgeCategory\n  stages\n  knowledgeScope\n  titleAnchor\n  patientNoteEid\n  updatedDate\n  tipsAndLinks {\n    description\n    url\n    additional\n    __typename\n  }\n  content {\n    ...particleFields\n    __typename\n  }\n  references {\n    ... on ArticleReference {\n      eid\n      __typename\n    }\n    ... on AnthologyReference {\n      eid\n      __typename\n    }\n    ... on BookReference {\n      eid\n      __typename\n    }\n    ... on UrlReference {\n      eid\n      __typename\n    }\n    ... on WebMdReference {\n      eid\n      __typename\n    }\n    ... on MiscReference {\n      eid\n      __typename\n    }\n    ... on UpToDateReference {\n      eid\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment particleFields on Particle {\n  __typename\n  eid\n  partType\n  textType\n  globalStyles\n  title\n  titleReferenceMarkup\n  abstract\n  content\n  isSubParticle\n  titleAnchors\n  media {\n    ...mediaFragment\n    __typename\n  }\n}\n\nfragment mediaFragment on MediaAsset {\n  __typename\n  eid\n  title\n  editorialLink {\n    __typename\n    ... on EditorialUrl {\n      url\n      __typename\n    }\n    ... on ForbiddenLink {\n      isForbidden\n      __typename\n    }\n  }\n  description\n  canonicalUrl\n  aspectRatio\n  overlayUrl\n  externalAddition {\n    __typename\n    ... on ExternalAddition {\n      type\n      url\n      fallbackUrl\n      __typename\n    }\n    ... on BlockedExternalAddition {\n      type\n      __typename\n    }\n  }\n  multilayerAsset\n  copyright {\n    __typename\n    eid\n    html\n  }\n}\n"}]

        with httpx.Client() as client:
            for cookie in cookies:
                client.cookies.set(cookie['name'], cookie['value'])
                client.get(article_url)
                response = client.post('https://www.amboss.com/de/api/graphql', json=payload)
        # expand_all_url = 'https://api.getblueshift.com/unity.gif?t=1685916227&e=article_expand_all_sections&r=&z=889453&x=393dd1b011e8c2bdb066696d257c3bc5&k=c67dca9f-2d3a-4a6e-b7bf-416968abe82f&u=https://next.amboss.com/de/courses/NS0--2/hVac8j/article/bM0HMg&article_xid=bM0HMg&article_title=Subclavian-Steal-Syndrom&_bsft_source=segment.com&customer_id=kTDamId5&anonymousId=c67dca9f-2d3a-4a6e-b7bf-416968abe82f'
        # expand_all_url2 = 'https://www.amboss.com/us/api/sprx/v1/t'
        # payload2 = {"timestamp":"2023-06-04T22:03:46.640Z","integrations":{"All":False,"Blueshift":True,"Braze Web Mode (Actions)":True,"Bunchbox":True,"Facebook Conversions API (Actions)":True,"Datadog":True,"Facebook Pixel":True,"Facebook Social Plugins":True,"Google AdWords New":True,"Google Analytics":True,"Google Analytics 4":True,"Google Tag Manager":True,"Hotjar":True,"HubSpot Forms":True,"Optimizely":True,"Podigee":True,"Segment.io":True,"Sentry":True,"Twitter Ads":True,"YouTube Video":True,"Zendesk":True,"cloudfront.net":True,"Jotform":True},"userId":"kTDamId5","anonymousId":"c67dca9f-2d3a-4a6e-b7bf-416968abe82f","event":"article_expand_all_sections","type":"track","properties":{"article_xid":"bM0HMg","article_title":"Subclavian-Steal-Syndrom"},"context":{"namespace":"German","app":{"name":"next","release":"ui-amboss@master-5056"},"traits":{"stage":"clinic","features":["dashboard","library","search","question_session","cases","labs","articles","amboss_logo_redirect","learning_cards_split_view","search_split_view","custom_session_creation","tutor_session_creation","session_history","analysis","toggle_nav_floating_button","courses","auditor","progress_bundle","progress_course","pharma_web","article_adjustable_font_size","bundle_pickup","pharma_android","pharma_ios","complete_profile","completed_bundle","extensions","pharma_search_survey","new_analysis","new_analysis_tutorial","dashboard_grid_layout","dark_mode_article","access_gateway","dosage_tooltip_onboarding","pharma_offline_enabled_beta1","user_profile_page","auth_sso","show_user_profile_notification","search_history","search_related_answers","tutor_sessions_page","can_edit_same_university_tutor_sessions","search_media_filters","stripe_shop","braze_content_cards","enable_mode_switcher","stripe_subscriptions"]},"Google Analytics":{"clientId":"GA1.1.292816021.1685474424"},"page":{"path":"/de/courses/NS0--2/hVac8j/article/bM0HMg","referrer":"","search":"","title":"Subclavian-Steal-Syndrom - AMBOSS","url":"https://next.amboss.com/de/courses/NS0--2/hVac8j/article/bM0HMg"},"userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0","locale":"en-US","library":{"name":"analytics.js","version":"next-1.51.6"}},"messageId":"ajs-next-d5dd159637ac670980eb394b786f778e","writeKey":"Blw9JtSqDecdRHdx2TBvnNPVIMKSnJC6","sentAt":"2023-06-04T22:03:47.063Z","_metadata":{"bundled":["Blueshift","Facebook Pixel","Google AdWords New","Google Tag Manager","Segment.io","Twitter Ads"],"unbundled":["Google Analytics"],"bundledIds":["61add2d180a0b1b76dfb66a5","616e78a88a2fcaf3ebc07a25","61a750c6162d314b0b8b15de","634e6440b8512f9c4f57c348","61a752a2c59c401a7968ce76"]}}
            json_data = response.json()
            # formatted_json = json.dumps(json_data, indent=2)
            # print(formatted_json)
            return json_data

    def parse(self, json_data):
        json_article = json_data[4]
        formated_json = json.dumps(json_article, indent=2)
        print(formated_json)

    def main(self):
        # print(f'Preaparation...')
        # driver = self.webdriversetup()
        # cookies = self.get_cookies(driver)
        # print(cookies)
        cookies = [{'name': 'AMBOSS_CONSENT', 'value': '{"Blueshift":true,"Braze":true,"Bunchbox":true,"Conversions API":true,"Datadog":true,"Facebook Pixel":true,"Facebook Social Plugins":true,"Google Ads":true,"Google Analytics":true,"Google Analytics 4":true,"Google Tag Manager":true,"Hotjar":true,"HubSpot Forms":true,"Optimizely":true,"Podigee":true,"Segment":true,"Sentry":true,"Twitter Advertising":true,"YouTube Video":true,"Zendesk":true,"cloudfront.net":true,"Jotform":true}', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1729130284, 'sameSite': 'None'}, {'name': '_hjSessionUser_1507086', 'value': 'eyJpZCI6IjU0NzZjZWYzLWQyZGMtNTgwNS05ODIxLTkxZWU2YzkxZmUwYyIsImNyZWF0ZWQiOjE2ODU5MzAyODU2ODYsImV4aXN0aW5nIjpmYWxzZX0=', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1717466285, 'sameSite': 'None'}, {'name': '_hjFirstSeen', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1685932085, 'sameSite': 'None'}, {'name': '_hjIncludedInSessionSample_1507086', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1685930405, 'sameSite': 'None'}, {'name': '_hjSession_1507086', 'value': 'eyJpZCI6IjBlMTJjZDk1LTJhN2MtNGJiZC1iY2YxLWY4ZmY0MTEzMjJlOCIsImNyZWF0ZWQiOjE2ODU5MzAyODU2ODcsImluU2FtcGxlIjp0cnVlfQ==', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1685932085, 'sameSite': 'None'}, {'name': '_hjAbsoluteSessionInProgress', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1685932085, 'sameSite': 'None'}, {'name': 'next_auth_amboss_de', 'value': '73c7a7d067065b17949def6fa6fe2d4d', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': True, 'expiry': 1717552685, 'sameSite': 'None'}, {'name': 'ajs_anonymous_id', 'value': '905454ab-1bf4-4c6d-b43c-a08990bc063c', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1717466288, 'sameSite': 'Lax'}, {'name': '_dd_s', 'value': 'logs=1&id=a536a42f-3fb5-42ac-b463-266d30aa2b2b&created=1685930284855&expire=1685931188351', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1685931188, 'sameSite': 'None'}]
        article_url = input('Please copy url of the article: ')
        json_data = self.scrape(article_url, cookies)
        self.parse(json_data)

if __name__ == '__main__':
    s = AmbossScraper()
    s.main()
import httpx
from selectolax.parser import HTMLParser
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import creds
from dataclasses import dataclass
import json
import base64


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
        ff_opt.add_argument('-headless')
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
            json_data = response.json()
            return json_data

    def parse(self, json_data):
        json_article = json_data[4]['data']['currentUserArticles'][0]['article']
        formatted_json = json.dumps(json_article, indent=2)
        print(formatted_json)
        title = json_article['title'].strip()
        print(title)

        synonyms_list = json_article['synonyms']
        synonyms = ', '.join(synonyms_list)
        print(synonyms)

        updated_date = json_article['updatedDate']
        print(updated_date)

        for i in range(len(json_article['content'])):
            print(f'==================={i}====================')
            nav = json_article['content'][i]['title']
            content = HTMLParser(json_article['content'][i]['content'])
            # elements = content.css('p, span.api.explanation, span[data-type="highlight"], span.leitwort, span[data-type="image"], li')
            elements = content.css(
                'p, p > span.api.explanation, p > span.leitwort, p > span[data-type="image"], p > span[data-type="highlight"], li')

            print(nav)
            count = 1
            span_explanations = []
            for element in elements:
                if element.tag == 'p':
                    p = element.text().strip()
                    print(p)
                elif element.tag == 'a':
                    a = element.text().strip()
                    print(a)
                elif element.tag == 'span':
                    if element.attributes['data-type'] == 'image':
                        img = element.attributes['data-source']
                        print(img)
                    elif element.attributes['class'] == 'api explanation':
                        base64_string = element.attributes['data-content']
                        decoded_bytes = base64.b64decode(base64_string)
                        decoded_string = decoded_bytes.decode('utf-8')
                        tree = HTMLParser(decoded_string).text().strip()
                        span_explanations.append({str(count): tree})
                        count += 1
                        print(span_explanations)
                        # for i, span_explanation in enumerate(tree):
                        #     span_explanations.append({str(i): span_explanation}.copy())
                        # print(span_explanations)
                    # elif element.attributes['class'] == 'api dictionary':
                    #     span_dictionary = element.text()
                    #     print(span_dictionary)
                    elif element.attributes['class'] == 'leitwort':
                        span_leitwort = element.text()
                        print(span_leitwort)
                elif element.tag == 'li':
                    li = element.text()
                    print(li)

        contents = []
        # for i in range(len(json_article['data']['currentUserArticles'][0]['article']['content'])):
        #     content = HTMLParser(json_article['data']['currentUserArticles'][0]['article']['content'][i]['content']).text().strip()
        #     contents.append(content)
        # main_article = ''.join(contents)
        # print(abstract)
        # print('===================================')
        # print(main_article)

    def main(self):
        # print(f'Preaparation...')
        # driver = self.webdriversetup()
        # cookies = self.get_cookies(driver)
        # print(cookies)
        cookies = [{'name': 'AMBOSS_CONSENT', 'value': '{"Blueshift":true,"Braze":true,"Bunchbox":true,"Conversions API":true,"Datadog":true,"Facebook Pixel":true,"Facebook Social Plugins":true,"Google Ads":true,"Google Analytics":true,"Google Analytics 4":true,"Google Tag Manager":true,"Hotjar":true,"HubSpot Forms":true,"Optimizely":true,"Podigee":true,"Segment":true,"Sentry":true,"Twitter Advertising":true,"YouTube Video":true,"Zendesk":true,"cloudfront.net":true,"Jotform":true}', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1729227289, 'sameSite': 'None'}, {'name': '_hjFirstSeen', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1686029090, 'sameSite': 'None'}, {'name': 'next_auth_amboss_de', 'value': '73c7a7d067065b17949def6fa6fe2d4d', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': True, 'expiry': 1717649690, 'sameSite': 'None'}, {'name': '_dd_s', 'value': 'logs=1&id=d4fa63af-eb22-440d-ba14-b1e58cefe3ff&created=1686027289635&expire=1686028193428', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1686028193, 'sameSite': 'None'}, {'name': '_bb', 'value': '647ebc1ef972609e54fe224a', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1749099294, 'sameSite': 'None'}, {'name': 'ajs_anonymous_id', 'value': 'dbba0acb-bebe-45fb-a0e9-413a38734915', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1717563295, 'sameSite': 'Lax'}, {'name': '_hjSessionUser_1507086', 'value': 'eyJpZCI6ImU1ZWUyYjlmLTM4OGQtNTNlMC1hNmQ5LWI1ZmZjZDhhN2JmMyIsImNyZWF0ZWQiOjE2ODYwMjcyOTA4MTIsImV4aXN0aW5nIjp0cnVlfQ==', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1717563295, 'sameSite': 'None'}, {'name': '_hjSession_1507086', 'value': 'eyJpZCI6IjQ1MTRmNjdlLTEwMjQtNDVmMC1hNzE3LWFlNjY2MGY1NTA0YiIsImNyZWF0ZWQiOjE2ODYwMjcyOTA4MTMsImluU2FtcGxlIjp0cnVlfQ==', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1686029095, 'sameSite': 'None'}, {'name': '_hjIncludedInSessionSample_1507086', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1686027415, 'sameSite': 'None'}, {'name': '_hjAbsoluteSessionInProgress', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1686029095, 'sameSite': 'None'}, {'name': '_hjHasCachedUserAttributes', 'value': 'true', 'path': '/', 'domain': 'next.amboss.com', 'secure': True, 'httpOnly': False, 'sameSite': 'None'}]
        article_url = input('Please copy url of the article: ')
        json_data = self.scrape(article_url, cookies)
        self.parse(json_data)

if __name__ == '__main__':
    s = AmbossScraper()
    s.main()
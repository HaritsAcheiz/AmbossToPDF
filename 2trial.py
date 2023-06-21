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
import os
from fpdf import FPDF, XPos, YPos
import shutil
from PIL import Image
from xhtml2pdf import pisa             # import python module

def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err


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

    def expand(self, html):
        doc = HTMLParser(html)
        span_elements = doc.css('span.api.explanation')
        for element in span_elements:
            base64_string = element.attributes['data-content']
            decoded_bytes = base64.b64decode(base64_string)
            decoded_string = decoded_bytes.decode('utf-8')
            decoded_content = f"(** {HTMLParser(decoded_string).text().strip()} **)"
            # Create a new text node with the data-content value
            new_text = HTMLParser(f'<text>{decoded_content}</text>').root
            # Replace the <span> element with the new text node
            element.replace_with(new_text)

        # Get the updated HTML
        updated_html = doc.html
        return updated_html

    def parse(self, json_data):
        pdf = FPDF(orientation='P', unit='pt', format='A4')
        pdf.add_font('EpocaPro', style='', fname='fonts/EpocaPro-Regular.ttf')
        pdf.add_font('EpocaPro', style='B', fname='fonts/EpocaPro-Bold.ttf')
        pdf.add_font('EpocaPro', style='I', fname='fonts/EpocaPro-Italic.ttf')
        pdf.add_page()

        max_width = pdf.w - 2 * pdf.l_margin

        json_article = json_data[4]['data']['currentUserArticles'][0]['article']
        formatted_json = json.dumps(json_article, indent=2)
        print(formatted_json)

        # title
        title = json_article['title'].strip()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(family='EpocaPro', style='B', size=16)
        pdf.multi_cell(w=max_width, h=18, txt=title, align='l')

        #synonyms
        synonyms_list = json_article['synonyms']
        synonyms = f"({', '.join(synonyms_list)})"
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(family='EpocaPro', style='I', size=14)
        pdf.multi_cell(w=max_width, h=14, txt=synonyms, align='l')

        #updated_date
        updated_date = f"Zuletzt bearbeitet: {json_article['updatedDate']}"
        pdf.set_text_color(139, 139, 139)
        pdf.set_font(family='EpocaPro', style='', size=14)
        pdf.multi_cell(w=max_width, h=14, txt=updated_date, align='l')
        contents = []
        for i in range(len(json_article['content'])):
            nav = json_article['content'][i]['title']
            pdf.set_text_color(50, 50, 50)
            pdf.set_font(family='EpocaPro', style='B', size=14)
            pdf.set_fill_color(211, 211, 211)
            pdf.cell(w=max_width, h=16, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.multi_cell(w=max_width, h=14, txt=synonyms, align='l')
            pdf.cell(w=max_width, h=16, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            contents.append(self.expand(HTMLParser(json_article['content'][i]['content']).html))
        content = ''.join(contents)
        pisa.showLogging()
        convert_html_to_pdf(content, 'coba')
        pdf.output(f'{title}.pdf')

    def main(self):
        # print(f'Preaparation...')
        # driver = self.webdriversetup()
        # cookies = self.get_cookies(driver)
        # print(cookies)
        cookies = [{'name': 'AMBOSS_CONSENT', 'value': '{"Blueshift":true,"Braze":true,"Bunchbox":true,"Conversions API":true,"Datadog":true,"Facebook Pixel":true,"Facebook Social Plugins":true,"Google Ads":true,"Google Analytics":true,"Google Analytics 4":true,"Google Tag Manager":true,"Hotjar":true,"HubSpot Forms":true,"Optimizely":true,"Podigee":true,"Segment":true,"Sentry":true,"Twitter Advertising":true,"YouTube Video":true,"Zendesk":true,"cloudfront.net":true,"Jotform":true}', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1730233418, 'sameSite': 'None'}, {'name': '_hjSessionUser_1507086', 'value': 'eyJpZCI6ImE1MmI4MDU0LWFlNjQtNTBiNy1hZTc4LTA3M2MyNGYxOTdiYyIsImNyZWF0ZWQiOjE2ODcwMzM0MTg5MDIsImV4aXN0aW5nIjpmYWxzZX0=', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1718569418, 'sameSite': 'None'}, {'name': '_hjFirstSeen', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': '_hjIncludedInSessionSample_1507086', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687033538, 'sameSite': 'None'}, {'name': '_hjSession_1507086', 'value': 'eyJpZCI6IjBhNzY4NzIyLWQyNzQtNGE2ZC04MDc1LWFmNjJjMWQyZjA2YyIsImNyZWF0ZWQiOjE2ODcwMzM0MTg5MDUsImluU2FtcGxlIjpmYWxzZX0=', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': '_hjAbsoluteSessionInProgress', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': 'next_auth_amboss_de', 'value': '0fbe98c2e6cde2968670fb8830f30014', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': True, 'expiry': 1718655814, 'sameSite': 'None'}, {'name': 'ajs_anonymous_id', 'value': 'f3da5ae2-d64b-4def-b997-c17a67233fc9', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1718569421, 'sameSite': 'Lax'}, {'name': '_dd_s', 'value': 'logs=1&id=b3bcef60-9186-4495-9dd9-ea648ed3bb17&created=1687033418257&expire=1687034321943', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687034321, 'sameSite': 'None'}, {'name': '_bb', 'value': '648e164f16ae671935f629b2', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1750105423, 'sameSite': 'None'}]
        article_url = input('Please copy url of the article: ')
        json_data = self.scrape(article_url, cookies)
        self.parse(json_data)


if __name__ == '__main__':
    s = AmbossScraper()
    s.main()
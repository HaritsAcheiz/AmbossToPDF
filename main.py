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
        data = []
        json_article = json_data[4]['data']['currentUserArticles'][0]['article']
        formatted_json = json.dumps(json_article, indent=2)
        print(formatted_json)
        title = json_article['title'].strip()
        data.append({'title': title})

        synonyms_list = json_article['synonyms']
        synonyms = f"({', '.join(synonyms_list)})"
        data.append({'synonyms': synonyms})

        updated_date = f"Zuletzt bearbeitet: {json_article['updatedDate']}"
        data.append({'updated_date': updated_date})

        for i in range(len(json_article['content'])):
            # try:
            #     if json_article['content'][i]['media'][1]['editorialLink']['isForbidden'] == True:
            #         pass
            # except:
            nav = json_article['content'][i]['title']
            data.append({'nav': nav})

            content = self.expand(HTMLParser(json_article['content'][i]['content']).html)
            expanded_content = HTMLParser(content)
            print(expanded_content.html)
            elements = expanded_content.css('*')

            for element in elements:
                if element.tag == 'p':
                    if element.css_first('span.case_text'):
                        continue
                    elif element.css_first('span.merke'):
                        continue
                    elif element.css_first('span.merkspruch'):
                        continue
                    elif element.parent.tag == 'span':
                        continue
                    elif element.parent.tag == 'li':
                        continue
                    else:
                        p = element.text()
                        data.append({'p': p})

                elif element.tag == 'span':
                    try:
                        if element.attributes['data-type'] == 'image':
                            url = element.attributes['data-source']
                            base64_string = element.attributes['data-title']
                            decoded_bytes = base64.b64decode(base64_string)
                            decoded_string = decoded_bytes.decode('utf-8')
                            title = HTMLParser(decoded_string).text().strip()
                            base64_string = element.attributes['data-description']
                            decoded_bytes = base64.b64decode(base64_string)
                            decoded_string = decoded_bytes.decode('utf-8')
                            desc = HTMLParser(decoded_string).text().strip()
                            data.append({'img': {'url': url, 'title': title, 'desc': desc}})

                    except:
                        if 'case_text' in element.attributes['class']:
                            span_case_text = element.text().strip()
                            data.append({'span_case_text': span_case_text})
                        elif 'merke' in element.attributes['class']:
                            span_merke = element.text().strip()
                            data.append({'span_merke': span_merke})
                        elif 'merkspruch' in element.attributes['class']:
                            span_merkspruch = element.text().strip()
                            data.append({'span_merkspruch': span_merkspruch})
                        else:
                            continue

                elif element.tag == 'li':
                    if element.css_first('span.leitwort'):
                        li_leitwort = element.text().strip().split('\n')[0]
                        data.append({'li_leitwort': li_leitwort})
                    # elif element.child.tag == 'ul':
                    #     pass
                    elif len(element.css('li')) > 1 and not element.css_first('span.leitwort'):
                        print(element.css('li'))
                        continue
                    else:
                        li = element.text().strip()
                        data.append({'li': li})

                # elif element.tag == 'li':
                #     if element.css_first('span.leitwort'):
                #         li1 = element.text().strip().split('\n')[0]
                #         data.append({'li1': li1})
                #     elif len(element.css('li')) > 1:
                #         li_children = element.text().split('n')
                #         if len(li_children) > 1:
                #             li_grandchildren = element.text().split('n')
                #             if len(li_grandchildren) > 1:
                #                 continue
                #             else:
                #                 li3 = li_grandchildren[0]
                #                 data.append({'li3': li3})
                #         else:
                #             li2 = li_children[0]
                #             data.append({'li2': li2})
                #     else:
                #         li1 = element.text().strip()
                #         data.append({'li1': li1})


                elif element.tag == 'h2':
                    h2 = element.text().strip()
                    data.append({'h2': h2})

                elif element.tag == 'h3':
                    h3 = element.text().strip()
                    data.append({'h3': h3})

                elif element.tag == 'table':
                    # rows = element.css('tr')
                    # for row in rows:
                    #     cells = row.css('td')
                    #     cell_content = []
                    #     for cell in cells:
                    #         cell_content.append(cell.text().strip())
                    # data.append({'table': cell_content})
                        #     pdf.cell(40, 10, str(cell.text.strip()), 1)
                        # pdf.ln()
                    table = element.html
                    data.append({'table': table})

        return data

    def download_img(self, data):
        urls = [item['img']['url'] for item in data if item.get('img')]

        folderpath = os.path.join(os.getcwd(), 'images')
        if os.path.exists(folderpath):
            shutil.rmtree(folderpath)
        os.makedirs(folderpath, exist_ok=True)

        for url in urls:
            with httpx.Client() as client:
                response = client.get(url)

            filename = url.split("/")[-1]
            filepath = os.path.join(folderpath, filename)
            with open(filepath, "wb") as file:
                file.write(response.content)

    def create_pdf(self, data):
        self.download_img(data)
        pdf = FPDF(orientation='P', unit='pt', format='A4')
        pdf.add_font('EpocaPro', style='', fname='fonts/EpocaPro-Regular.ttf')
        pdf.add_font('EpocaPro', style='B', fname='fonts/EpocaPro-Bold.ttf')
        pdf.add_font('EpocaPro', style='I', fname='fonts/EpocaPro-Italic.ttf')
        max_width = pdf.w - 2 * pdf.l_margin
        pdf.add_page()
        for item in data:
            if item.get('title'):
                output_name = item.get('title')
                pdf.set_text_color(0, 0, 0)
                pdf.set_font(family='EpocaPro', style='B', size=16)
                pdf.multi_cell(w=max_width, h=18, txt=item.get('title'), align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('synonyms'):
                pdf.set_text_color(0, 0, 0)
                pdf.set_font(family='EpocaPro', style='I', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('synonyms'), align='l',new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('updated_date'):
                pdf.set_text_color(139, 139, 139)
                pdf.set_font(family='EpocaPro', style='', size=14)
                pdf.cell(w=max_width, h=16, txt=item.get('updated_date'), align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('nav'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.set_fill_color(211, 211, 211)
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('nav'), align='l', fill=True)
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('p'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('p').replace('→', '->'), align='J')
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('p_case_text'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=0, h=14, txt=item.get('p_case_text').replace('→', '->'), align='J', border=1)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('img'):
                image_name = item['img']['url'].split('/')[-1]
                img = Image.open(os.path.join(os.getcwd(), 'images', image_name))
                img.close()
                y_before_img = pdf.get_y()
                page_before_img = pdf.page_no()
                img_width = img.width if img.width <= 250 else 250
                pdf.image(os.path.join(os.getcwd(), 'images', image_name), w=img_width)
                y_after_img = pdf.get_y()
                page_after_img = pdf.page_no()
                pdf.set_text_color(255, 255, 255)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.set_fill_color(47, 79, 79)
                if page_after_img == page_before_img:
                    pdf.set_xy(300, y_before_img)
                else:
                    pdf.set_xy(300, 29)
                pdf.multi_cell(w=265, h=14, txt=f"{item['img']['title']}\n\n{item['img']['desc'].replace('→', '->')}", align='l', fill=True)
                y_after_desc = pdf.get_y()
                if y_after_img > y_after_desc:
                    pdf.set_xy(0, y_after_img)
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('span_case_text'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_case_text').replace('→', '->'), align='J', border=1)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('span_merke'):
                pdf.set_text_color(0, 153, 76)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.set_fill_color(204, 255, 229)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_merke').replace('→', '->'), align='J', border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('span_merkspruch'):
                pdf.set_text_color(0, 76, 153)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.set_fill_color(204, 229, 255)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_merkspruch').replace('→', '->'), align='J', border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # elif item.get('li1'):
            #     pdf.set_text_color(50, 50, 50)
            #     pdf.set_font(family='EpocaPro', style='', size=12)
            #     pdf.cell(w=16, h=14, txt=f"\u2022", new_x=XPos.RIGHT, new_y=YPos.TOP)
            #     pdf.multi_cell(w=0, h=14, txt=item.get('li1').replace('→', '->'), align='J')
            # elif item.get('li2'):
            #     pdf.set_text_color(50, 50, 50)
            #     pdf.set_font(family='EpocaPro', style='', size=12)
            #     pdf.cell(w=16, h=14, txt=f"   \u2022", new_x=XPos.RIGHT, new_y=YPos.TOP)
            #     pdf.multi_cell(w=0, h=14, txt=item.get('li2').replace('→', '->'), align='J')
            # elif item.get('li3'):
            #     pdf.set_text_color(50, 50, 50)
            #     pdf.set_font(family='EpocaPro', style='', size=12)
            #     pdf.cell(w=16, h=14, txt=f"      \u2022", new_x=XPos.RIGHT, new_y=YPos.TOP)
            #     pdf.multi_cell(w=0, h=14, txt=item.get('li3').replace('→', '->'), align='J')
            elif item.get('li_leitwort'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.cell(w=16, h=14, txt=f"\u2022", new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('li_leitwort').replace('→', '->'), align='J', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('li'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.cell(w=16, h=14, txt=f"   \u2022", new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('li').replace('→', '->'), align='J', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('h2'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('h2'), align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('h3'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('h3'), align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            elif item.get('table'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=4)
                pdf.write_html(item.get('table'), table_line_separators=True)
                # cell_contents = item.get('table')
                # for cell_content in cell_contents:
                #     pdf.multi_cell(w=50, h=16, txt=cell_content, align='l', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                # pdf.ln()
        pdf.output(f'{output_name}.pdf')

    def main(self):
        # print(f'Preaparation...')
        # driver = self.webdriversetup()
        # cookies = self.get_cookies(driver)
        # print(cookies)
        cookies = [{'name': 'AMBOSS_CONSENT', 'value': '{"Blueshift":true,"Braze":true,"Bunchbox":true,"Conversions API":true,"Datadog":true,"Facebook Pixel":true,"Facebook Social Plugins":true,"Google Ads":true,"Google Analytics":true,"Google Analytics 4":true,"Google Tag Manager":true,"Hotjar":true,"HubSpot Forms":true,"Optimizely":true,"Podigee":true,"Segment":true,"Sentry":true,"Twitter Advertising":true,"YouTube Video":true,"Zendesk":true,"cloudfront.net":true,"Jotform":true}', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1730233418, 'sameSite': 'None'}, {'name': '_hjSessionUser_1507086', 'value': 'eyJpZCI6ImE1MmI4MDU0LWFlNjQtNTBiNy1hZTc4LTA3M2MyNGYxOTdiYyIsImNyZWF0ZWQiOjE2ODcwMzM0MTg5MDIsImV4aXN0aW5nIjpmYWxzZX0=', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1718569418, 'sameSite': 'None'}, {'name': '_hjFirstSeen', 'value': '1', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': '_hjIncludedInSessionSample_1507086', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687033538, 'sameSite': 'None'}, {'name': '_hjSession_1507086', 'value': 'eyJpZCI6IjBhNzY4NzIyLWQyNzQtNGE2ZC04MDc1LWFmNjJjMWQyZjA2YyIsImNyZWF0ZWQiOjE2ODcwMzM0MTg5MDUsImluU2FtcGxlIjpmYWxzZX0=', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': '_hjAbsoluteSessionInProgress', 'value': '0', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687035218, 'sameSite': 'None'}, {'name': 'next_auth_amboss_de', 'value': '0fbe98c2e6cde2968670fb8830f30014', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': True, 'expiry': 1718655814, 'sameSite': 'None'}, {'name': 'ajs_anonymous_id', 'value': 'f3da5ae2-d64b-4def-b997-c17a67233fc9', 'path': '/', 'domain': '.amboss.com', 'secure': False, 'httpOnly': False, 'expiry': 1718569421, 'sameSite': 'Lax'}, {'name': '_dd_s', 'value': 'logs=1&id=b3bcef60-9186-4495-9dd9-ea648ed3bb17&created=1687033418257&expire=1687034321943', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1687034321, 'sameSite': 'None'}, {'name': '_bb', 'value': '648e164f16ae671935f629b2', 'path': '/', 'domain': '.amboss.com', 'secure': True, 'httpOnly': False, 'expiry': 1750105423, 'sameSite': 'None'}]
        article_url = input('Please copy url of the article: ')
        json_data = self.scrape(article_url, cookies)
        data = self.parse(json_data)
        self.create_pdf(data)


if __name__ == '__main__':
    s = AmbossScraper()
    s.main()
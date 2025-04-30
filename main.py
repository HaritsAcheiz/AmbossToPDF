import httpx
from selectolax.parser import HTMLParser
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import creds
import warnings
from dataclasses import dataclass
import json
import base64
import os
from fpdf import FPDF
import shutil
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

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
        wait = WebDriverWait(driver, 5)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'button.layers_button__iCDH4:nth-child(2)'))).click()
        wait = WebDriverWait(driver, 20)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '.css-1eewvb8-StyledInput'))).send_keys(creds.email + Keys.TAB + creds.password + Keys.RETURN)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, '#search-input')))
        cookies = driver.get_cookies()
        driver.close()
        return cookies

    def scrape(self, article_url, cookies):
        param = article_url.split("/")
        eid = param[5]
        
        payload = [{"operationName":"channelNotificationsQuery","variables":{"channels":["userMenu"],"limit":1},"query":"query channelNotificationsQuery($channels: [String!]!, $limit: Int, $showDismissed: Boolean) {\n  currentUserNotification(\n    channels: $channels\n    limit: $limit\n    showDismissed: $showDismissed\n  ) {\n    uuid\n    class\n    payload\n    dismissedAt\n    __typename\n  }\n}"},{"operationName":"latestNonStudyAnalysisQuestionSessions","variables":{"first":5},"query":"query latestNonStudyAnalysisQuestionSessions($first: Int!, $after: String) {\n  currentUserQuestionSessions(first: $first, after: $after) {\n    edges {\n      node {\n        eid\n        userBundle {\n          eid\n          bundle {\n            eid\n            course {\n              eid\n              category\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"},{"operationName":"channelNotificationsQuery","variables":{"channels":["global"]},"query":"query channelNotificationsQuery($channels: [String!]!, $limit: Int, $showDismissed: Boolean) {\n  currentUserNotification(\n    channels: $channels\n    limit: $limit\n    showDismissed: $showDismissed\n  ) {\n    uuid\n    class\n    payload\n    dismissedAt\n    __typename\n  }\n}"},{"operationName":"articleQuery","variables":{"eids":[eid]},"query":"query articleQuery($eids: [ID!]!) {\n  currentUserArticles(eids: $eids) {\n    eid\n    editorialLink {\n      ... on EditorialUrl {\n        url\n        __typename\n      }\n      ... on ForbiddenLink {\n        isForbidden\n        __typename\n      }\n      __typename\n    }\n    article {\n      ...articleFullFragment\n      __typename\n    }\n    isLearned\n    __typename\n  }\n}\n\nfragment mediaFragment on MediaAsset {\n  __typename\n  eid\n  title\n  editorialLink {\n    __typename\n    ... on EditorialUrl {\n      url\n      __typename\n    }\n    ... on ForbiddenLink {\n      isForbidden\n      __typename\n    }\n  }\n  description\n  canonicalUrl\n  aspectRatio\n  overlayUrl\n  externalAddition {\n    __typename\n    ... on ExternalAddition {\n      type\n      url\n      fallbackUrl\n      __typename\n    }\n    ... on BlockedExternalAddition {\n      type\n      __typename\n    }\n  }\n  multilayerAsset\n  copyright {\n    __typename\n    eid\n    html\n  }\n}\n\nfragment particleFields on Particle {\n  __typename\n  eid\n  partType\n  textType\n  globalStyles\n  title\n  titleReferenceMarkup\n  content\n  isSubParticle\n  titleAnchors\n  media {\n    ...mediaFragment\n    __typename\n  }\n}\n\nfragment articleFullFragment on Article {\n  __typename\n  eid\n  title\n  synonyms\n  abstract\n  knowledgeCategory\n  stages\n  knowledgeScope\n  titleAnchor\n  patientNoteEid\n  updatedDate\n  tipsAndLinks {\n    description\n    url\n    additional\n    __typename\n  }\n  content {\n    ...particleFields\n    __typename\n  }\n  references {\n    ... on ArticleReference {\n      eid\n      __typename\n    }\n    ... on AnthologyReference {\n      eid\n      __typename\n    }\n    ... on BookReference {\n      eid\n      __typename\n    }\n    ... on UrlReference {\n      eid\n      __typename\n    }\n    ... on WebMdReference {\n      eid\n      __typename\n    }\n    ... on MiscReference {\n      eid\n      __typename\n    }\n    ... on UpToDateReference {\n      eid\n      __typename\n    }\n    __typename\n  }\n}"},{"operationName":"userParticlesAndQuestionResultsQuery","variables":{"eids":[eid]},"query":"query userParticlesAndQuestionResultsQuery($eids: [ID!]!) {\n  currentUserArticles(eids: $eids) {\n    eid\n    article {\n      eid\n      __typename\n    }\n    userParticles {\n      ...userParticlesFragment\n      __typename\n    }\n    questionResults {\n      sessionEid\n      questionEid\n      isAnswerCorrect\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment userParticlesFragment on UserParticle {\n  particleEid\n  extension {\n    text\n    eid\n    ownerName\n    __typename\n  }\n  sharedExtensions {\n    text\n    eid\n    ownerName\n    __typename\n  }\n  __typename\n}"},{"operationName":"getUserStudyObjective","variables":{},"query":"query getUserStudyObjective {\n  currentStudyObjective {\n    eid\n    label\n    superset\n    __typename\n  }\n}"},{"operationName":"userConfigQuery","variables":{},"query":"query userConfigQuery {\n  currentUserConfig {\n    ...userConfigFragment\n    __typename\n  }\n}\n\nfragment taxonListFragment on Taxon {\n  eid\n  label\n  level\n  parentEid\n  __typename\n}\n\nfragment userConfigFragment on UserConfig {\n  examWhiteList {\n    ...taxonListFragment\n    __typename\n  }\n  hasConfirmedHealthCareProfession\n  __typename\n}"},{"operationName":"currentUserHighlightsOnParticles","variables":{"particleEids":[]},"query":"query currentUserHighlightsOnParticles($particleEids: [ID!]!) {\n  currentUserHighlightsOnParticles(particleEids: $particleEids) {\n    particleEid\n    highlights {\n      stampId\n      eid\n      text\n      color\n      updatedAt\n      starts\n      ends\n      __typename\n    }\n    __typename\n  }\n}"},{"operationName":"readArticleMutation","variables":{"articleEid":eid,"referrer":"library"},"query":"mutation readArticleMutation($articleEid: ID!, $referrer: ArticleReferrer) {\n  readArticle(articleEid: $articleEid, referrer: $referrer)\n}"},{"operationName":"channelNotificationsQuery","variables":{"channels":["userActionRequest"]},"query":"query channelNotificationsQuery($channels: [String!]!, $limit: Int, $showDismissed: Boolean) {\n  currentUserNotification(\n    channels: $channels\n    limit: $limit\n    showDismissed: $showDismissed\n  ) {\n    uuid\n    class\n    payload\n    dismissedAt\n    __typename\n  }\n}"}]


        with httpx.Client() as client:
            for cookie in cookies:
                client.cookies.set(cookie['name'], cookie['value'])
            resp = client.get(article_url)
            print(resp.status_code)
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
        print(json_data)
        json_article = json_data[3]['data']['currentUserArticles'][0]['article']
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
            nav = json_article['content'][i]['title']
            data.append({'nav': nav})

            content = self.expand(HTMLParser(json_article['content'][i]['content']).html)
            expanded_content = HTMLParser(content)
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
                    if element.css_first('ul') != None:
                        if element.css_first('li > ul > li > ul > li') != None:
                            li1 = element.text().split('\n')[0]
                            data.append({'li1': li1})
                        else:
                            li2 = element.text().split('\n')[0]
                            data.append({'li2': li2})
                    else:
                        li3 = element.text().strip()
                        data.append({'li3': li3})
                elif element.tag == 'h2':
                    h2 = element.text().strip()
                    data.append({'h2': h2})

                elif element.tag == 'h3':
                    h3 = element.text().strip()
                    data.append({'h3': h3})

                elif element.tag == 'table':
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

    def process_table_header(self, pdf, rows):
        # Initialize merged_cell_pos and merged_cell_width
        merged_cell_pos = 0  # or None, depending on your logic
        merged_cell_width = 0  # Initialize merged_cell_width

        # Get max rows
        for i, row in enumerate(rows):
            cells = row.css('th')
            colspans = []
            x = pdf.get_x()
            y = pdf.get_y()
            max_height = 0

            for cell in cells:
                colspan = int(cell.attributes.get("colspan", 1))
                colspans.append(colspan)
            count_of_col = len(colspans)  # Count of columns based on colspans

            if i == 0:
                for cell in cells:
                    colspan = int(cell.attributes.get("colspan", 1))
                    rowspan = int(cell.attributes.get("rowspan", 1))
                    content = cell.text().strip()

                    # Calculate cell width and height based on colspan and rowspan
                    line_height = pdf.font_size
                    cell_width = pdf.epw / count_of_col  # Calculate cell width
                    cell_height = line_height

                    if colspan == 2:
                        merged_cell_pos = pdf.x - pdf.l_margin
                        merged_cell_width = pdf.epw / count_of_col

                    if rowspan == 2:
                        cell_height = line_height * 2

                    # Set font
                    pdf.set_font(family='EpocaPro', style='', size=8)
                    pdf.set_text_color(0, 0, 0)

                    # Header
                    pdf.set_font(family='EpocaPro', style='B', size=8)

                    last_x = pdf.get_x()
                    last_y = pdf.get_y()
                    pdf.line(x + pdf.l_margin, y, x + pdf.l_margin, y + max_height)
                    pdf.multi_cell(w=cell_width, max_line_height=cell_height, txt=content, align='L')

                    if pdf.get_y() - y > max_height:
                        max_height = pdf.get_y() - y
                    pdf.set_xy(pdf.get_x(), last_y)
                    pdf.line(pdf.get_x(), y, pdf.get_x(), y + max_height)

                pdf.ln(line_height)
                pdf.line(x + pdf.l_margin, y, x + pdf.l_margin + cell_width * count_of_col, y)

            else:
                # Check if merged_cell_pos has been set
                if merged_cell_pos is not None:
                    pdf.cell(merged_cell_pos)
                else:
                    pdf.cell(0)  # Or handle the case where merged_cell_pos is not set

                for cell in cells:
                    colspan = int(cell.attributes.get("colspan", 1))
                    rowspan = int(cell.attributes.get("rowspan", 1))
                    content = cell.text().strip()

                    if colspan == 2:
                        merged_cell_pos = pdf.x - pdf.l_margin
                        merged_cell_width = pdf.epw / count_of_col

                    if rowspan == 2:
                        cell_height = line_height * 2

                    # Set font
                    pdf.set_font(family='EpocaPro', style='', size=8)

                    # Calculate cell width and height based on colspan and rowspan
                    if merged_cell_width > 0:
                        cell_width = merged_cell_width / (colspan * 2)
                    else:
                        print(f"Warning: merged_cell_width is {merged_cell_width}. Setting cell_width to minimum of 10.")
                        cell_width = 10  # Set a minimum width to avoid the error

                    # Debugging output
                    print(f"Cell Width: {cell_width}, Content: '{content}'")
                    
                    # Header
                    pdf.set_font(style='B')
                    pdf.set_text_color(0, 0, 0)
                    last_x = pdf.get_x()
                    last_y = pdf.get_y()

                    # Call multi_cell with the calculated cell_width
                    try:
                        pdf.multi_cell(w=cell_width, max_line_height=cell_height, txt=content, align='L')
                    except Exception as e:
                        print(f"Error while rendering cell: {e}")
                        # Optionally, you can set a fallback or skip this cell
                        continue

                    if pdf.get_y() - y > max_height:
                        max_height = pdf.get_y() - y
                    pdf.set_xy(pdf.get_x(), last_y)
                    pdf.line(pdf.get_x(), y, pdf.get_x(), y + max_height)

                pdf.ln(line_height)
                pdf.line(merged_cell_pos + pdf.l_margin, y, merged_cell_pos + pdf.l_margin + cell_width * count_of_col, y)
                pdf.line(merged_cell_pos + pdf.l_margin, y + max_height, merged_cell_pos + pdf.l_margin + cell_width * count_of_col, y + max_height)

            # Last border
            pdf.line(x + pdf.l_margin, y + max_height, x + pdf.l_margin + cell_width * count_of_col, y + max_height)

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
                pdf.multi_cell(w=max_width, h=18, txt=item.get('title'), align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('synonyms'):
                pdf.set_text_color(0, 0, 0)
                pdf.set_font(family='EpocaPro', style='I', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('synonyms'), align='l',new_x='LMARGIN', new_y='NEXT')
            elif item.get('updated_date'):
                pdf.set_text_color(139, 139, 139)
                pdf.set_font(family='EpocaPro', style='', size=14)
                pdf.cell(w=max_width, h=16, txt=item.get('updated_date'), align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('nav'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.set_fill_color(211, 211, 211)
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
                pdf.multi_cell(w=max_width, h=16, txt=item.get('nav'), align='l', fill=True)
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('p'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('p').replace('→', '->'), align='J')
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('p_case_text'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=0, h=14, txt=item.get('p_case_text').replace('→', '->'), align='J', border=1)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
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
                pdf.cell(w=max_width, h=16, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('span_case_text'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_case_text').replace('→', '->'), align='J', border=1)
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('span_merke'):
                pdf.set_text_color(0, 153, 76)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.set_fill_color(204, 255, 229)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_merke').replace('→', '->'), align='J', border=1, fill=True, new_x='LMARGIN', new_y='NEXT')
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('span_merkspruch'):
                pdf.set_text_color(0, 76, 153)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.set_fill_color(204, 229, 255)
                pdf.multi_cell(w=max_width, h=14, txt=item.get('span_merkspruch').replace('→', '->'), align='J', border=1, fill=True, new_x='LMARGIN', new_y='NEXT')
                pdf.cell(w=max_width, h=14, txt='', align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('li1'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.cell(w=16, h=14, txt=f"\u2022 ", new_x='END', new_y='LAST')
                pdf.multi_cell(w=max_width, h=14, txt=item.get('li1').replace('→', '->'), align='J', new_x='LMARGIN', new_y='NEXT')
            elif item.get('li2'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.cell(w=16, h=14, txt=f"   \u2022 ", new_x='END', new_y='LAST')
                pdf.multi_cell(w=max_width, h=14, txt=item.get('li2').replace('→', '->'), align='J', new_x='LMARGIN', new_y='NEXT')
            elif item.get('li3'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='', size=12)
                pdf.cell(w=max_width, h=14, txt=f"      \u2022", new_x='END', new_y='LAST')
                pdf.multi_cell(w=max_width, h=14, txt=item.get('li3').replace('→', '->'), align='J', new_x='LMARGIN', new_y='NEXT')
            elif item.get('h2'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('h2'), align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('h3'):
                pdf.set_text_color(50, 50, 50)
                pdf.set_font(family='EpocaPro', style='B', size=14)
                pdf.multi_cell(w=max_width, h=16, txt=item.get('h3'), align='l', new_x='LMARGIN', new_y='NEXT')
            elif item.get('table'):
                parser = HTMLParser(item.get('table'))
                table = parser.css_first("table")
                rows = table.css("thead > tr")
                self.process_table_header(pdf, rows)

        pdf.output(f'{output_name}.pdf')

    def main(self):
        print(f'Preaparation...')
        driver = self.webdriversetup()
        cookies = self.get_cookies(driver)
        if cookies:
            print('[+] Cookies grabbed.')
            print(cookies)
            article_url = input('Please copy url of the article: ')
            json_data = self.scrape(article_url, cookies)
            print('[+] Json scraped.')
            data = self.parse(json_data)
            print('[+] Article parsed.')
            self.create_pdf(data)
            print('[+] PDF Created.')



if __name__ == '__main__':
    s = AmbossScraper()
    s.main()

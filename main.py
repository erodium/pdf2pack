import fitz
import json

from bs4 import BeautifulSoup
from template import Template, JournalEntry

doc = fitz.open("pdfs/2.pdf")

html = ""
meta = {}

for page in doc:
    if page.number == 0:
        t = page.get_text().split("\n")
        meta['author'] = t[0]
        meta['title'] = t[1]
        meta['adventure'] = t[2]
        meta['tier'] = t[3]
    elif page.number > 1:
        html += page.get_text("xhtml")

print(meta)
adv = meta['adventure'].split("#")[1]
meta['season'] = adv[:1]
meta['scenario_number'] = adv[-3:].strip()
print(meta)


t = Template(adv_name=meta['title'], season=meta['season'], scenarionum=meta['scenario_number'])


with open("2.html", "w") as f:
    f.write(html)

with open("2.html") as f:
    soup = BeautifulSoup(f, 'html.parser')

p3_imgs = BeautifulSoup(doc[2].get_text('xhtml'), 'html.parser').find_all("img")
top_pic = p3_imgs[0]
bot_pic = p3_imgs[1]

# Get rid of the top and bottom banners, and all small images
for img in soup.find_all("img"):
    if img == top_pic or img == bot_pic or int(img.get("height")) <= 40:
        img.parent.decompose()


# Get rid of all the Title Strings (except 1)
passed_first_title = False
for h in soup.find_all("h1"):
    if h.b:
        if h.b.contents[0] == meta['title']:
            if passed_first_title:
                h.decompose()
            else:
                passed_first_title = True

# Get rid of all the PFS strings
for h in soup.find_all("h2"):
    if h.b:
        if h.b.contents[0] == "Pathfinder Society Scenario":
            h.decompose()

# Get rid of all the page numbers
page_nums = [x for x in range(0, doc.page_count)]
for h in soup.find_all("h1"):
    if h.b:
        if len(h.b.contents[0]) < 3 and int(h.b.contents[0]) in page_nums:
            h.decompose()

for h in soup.find_all("h3"):
    if h.b:
        if h.b.contents[0] == meta['author']:
            h.decompose()


cur_journ = None
cur_page = None
for tag in soup.find_all(["h1", "h2", "h3", "p"]):
    if tag.b and len(tag.b.contents) > 0:
        n = str(tag.b.contents[0])
    elif len(tag.contents) > 0:
        n = str(tag.contents[0])
    else:
        n = "no contents"
    if tag.name == "h1":
        if cur_journ:
            t.add_journal_entry(cur_journ)
        cur_journ = JournalEntry(n)
    elif tag.name == "h2" or tag.name == "h3":
        cur_journ.add_page(n)
        if len(tag.contents) > 1:
            cur_journ.add_text([str(tag)])
    elif tag.name == "p":
        cur_journ.add_text(str(tag))
t.add_journal_entry(cur_journ)


with open("2e.html", "w", encoding="utf=8") as f:
    f.write(soup.prettify())


with open("pfs102.db", "w") as f:
    f.write(str(t))

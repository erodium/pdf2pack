import json
import copy


def get_blank_template(t_name="blank_template"):
    with open(f"templates/{t_name}.json", encoding="utf-8") as f:
        template = json.load(f)
    return template


class Template:
    def __init__(self, adv_name="ADVNAME", season=0, scenarionum="00"):
        for k, v in get_blank_template().items():
            setattr(self, k, v)
        self.season = season
        self.scenario_num = scenarionum
        self._id = f"lPFS{season}{scenarionum}AdvPack00"
        self.name = adv_name
        self.folders = self.get_folder_set(season, scenarionum)
        self.num_journal_entries = 0

    def __str__(self):
        return json.dumps(self.__dict__, separators=(',', ':'))

    def get_folder_set(self, season, scen):
        folders = []
        with open("templates/folder.json", encoding="utf-8") as f:
            f_temp = json.load(f)
        for t in ["Scene", "Actor", "JournalEntry"]:
            prev_folder = None
            for i, nm in [(1, "Pathfinder Society"), (2, f"Season {season}"), (3, self.name)]:
                fid = f"lPFS{season}{scen}Fol{t[:5]}{i}"

                folder = copy.deepcopy(f_temp)
                folder['name'] = nm
                folder['folder'] = prev_folder
                folder['type'] = t
                folder['_id'] = fid
                folder['flags']['core']['sourceId'] = f"Folder.{fid}"
                folders.append(folder)
                prev_folder = fid
            setattr(self, f"{t.lower()}_folder", prev_folder)

        return folders

    def add_journal_entry(self, journal_entry):
        self.num_journal_entries += 1
        jnum = f"{self.num_journal_entries:02}"
        jid = f"lFPS{self.season}{self.scenario_num}Journal{jnum}"
        journal_entry.set_folder(self.journalentry_folder)
        journal_entry.set_id(jid)
        journal_entry.set_number(self.num_journal_entries)
        num_pages = 0
        for page in journal_entry.pages:
            num_pages += 1
            page['_id'] = f"lPFS{self.season}{self.scenario_num}JrnPg{num_pages:04}"
        self.journal.append(journal_entry.__dict__)


# t = Template()
# print(t)

class JournalEntry:
    def __init__(self, name="JournalName"):
        self.folder = None
        for k, v in get_blank_template("journal").items():
            setattr(self, k, v)
        self.name = name

    def set_folder(self, folder_id):
        self.folder = folder_id

    def set_id(self, jid):
        self._id = jid

    def add_page(self, name):
        p = get_blank_template("journal_page")
        p['name'] = name
        self.pages.append(p)

    def add_text(self, itemlist):
        if len(self.pages) == 0:
            self.add_page("blank")
        for item in itemlist:
            self.pages[-1]['text']['content'] += item

    def set_number(self, num):
        self.name = f"{num}. {self.name}"

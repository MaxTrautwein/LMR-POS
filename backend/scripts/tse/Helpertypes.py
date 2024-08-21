# Only use for Typing
class ProcessTyp:
    pass


# We should only really need that one
class ProcessTypBon(ProcessTyp):
    def __init__(self):
        self.name = "Kassenbeleg-V1"
        self.VorgangsTyp = "Beleg"  # Other Options don't apply to TSE
        self.BruttoSteuerumsaetze = ""
        self.Zahlungen = ""

    def getData(self) -> str:
        return f"{self.VorgangsTyp}^{self.BruttoSteuerumsaetze}^{self.Zahlungen}"

    # TODO: Add Typing "." as decimal point, 2 Decimals;
    # TODO: Ensure that unused -> "0.00"
    def SetBruttoSteuerumsaetze(self, Standard, Reduced, Avg_p24_1_nr3_UStG, Avg_p24_1_nr1_UStG, zero):
        self.BruttoSteuerumsaetze = f"{Standard}_{Reduced}_{Avg_p24_1_nr3_UStG}_{Avg_p24_1_nr1_UStG}_{zero}"

    # We only Support "Bar" & "EUR"
    def SetZahlungen(self, Total):
        # From the Examples it looks like ":EUR" at the end is optional if ony EUR is used
        self.Zahlungen = f"{Total}:Bar"

    # TODO how & when to set GV_TYP


# We should have no need for this, but it exists
class ProcessTypOrder(ProcessTyp):
    def __init__(self):
        self.name = "Bestellung-V1"
        self.data = ""

    def UpdateData(self, data: str = ""):
        self.data = data

    def getData(self) -> str:
        return self.data


# We should have no need for this, but it exists
class ProcessTypMisc(ProcessTyp):
    def __init__(self, data: str = ""):
        self.name = "SonstigerVorgang"
        self.data = data

    def UpdateData(self, data: str = ""):
        self.data = data

    def getData(self) -> str:
        return self.data

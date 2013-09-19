from supy import wrappedChain,utils

defaultColl=('jet_AntiKt4LCTopo_','')
#___________________________________________________________
class P4(wrappedChain.calculable) :
    def __init__(self, collection=defaultColl):
        self.p4=utils.LorentzV
        self.fixes = collection
        self.stash(["E", "pt", "eta", "phi", "m"])
    def update(self, _) :
        self.value = [self.p4(pt, eta, phi, m) for pt,eta,phi,m in zip(self.source[self.pt],
                                                                       self.source[self.eta],
                                                                       self.source[self.phi],
                                                                       self.source[self.m])]
class recJetP4(P4) :
    @property
    def name(self) : return 'recJetP4'
#___________________________________________________________
class Indices(wrappedChain.calculable) :
    def __init__(self, ptMin = None, etaMax = None) :
        self.ptMin = ptMin
        self.etaMax = etaMax
        self.moreName = ';'.join(filter(lambda x:x,
                                        ("pT>%g MeV"%ptMin if ptMin else '',
                                         "|eta|<%g"%etaMax if etaMax else '')))
    def update(self, _) :
        p4s = self.source['recJetP4']
        self.value = [i for i,j in enumerate(p4s)
                      if  ((not self.ptMin)  or j.pt() > self.ptMin) \
                      and ((not self.etaMax) or abs(j.eta()) < self.etaMax)]
class recJetIndices(Indices) :
    @property
    def name(self) : return 'recJetIndices'
#___________________________________________________________

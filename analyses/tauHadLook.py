#!/usr/bin/env python

# to be tested with Burt's workaround
# import sys
# sys.argv.append("-b")
# import ROOT as r
# r.gROOT.SetBatch(True)
# sys.argv.pop()

import supy
#supy.setupROOT()
import calculables,steps,samples

MeV2GeV = 1.0e+3
GeV=1.0e+3
TeV=1.0e+3*GeV

mcColl = ('mc_','')

class tauHadLook(supy.analysis) :
    def parameters(self) :
        objects = self.vary()
        leptons = self.vary()
        fields = [ "jet", "met", "muon", "electron",]
        objects['std'] =  dict(zip(fields, [("jet_AntiKt4LCTopo_",""),
                                            "MET_RefFinal_STVF_",
                                            ("mu_staco_",""),
                                            ("el_","")]))

        fieldsLepton =                           ['name', 'ptMin', 'etaMax',   'isoVar', 'isoType']
        leptons['muon'] = dict(zip(fieldsLepton, ['muon',      10,      2.4, 'ptcone30', 'relative']))
        jetPars = {'maxEta' : 2.5, 'minPt' : 20.0*GeV}
        return {
            'objects'  : objects,
            'lepton'   : leptons,
            'jetPars'  : jetPars
                }

    def listOfSteps(self,config) :
        obj = config["objects"]
        lepton = obj['muon']
        ssf, ssh = supy.steps.filters, supy.steps.histos
        hi, wi, wci = 'higgsIndices'.join(mcColl), 'wIndices'.join(mcColl), 'wChildrenIndices'.join(mcColl)
        stepsList = [
            supy.steps.printer.progressPrinter(),
            steps.gen.higgsDecay(),
            steps.gen.wDecay(),
            ssh.multiplicity('SignalLeptonIndices'.join(mcColl)),
            ssf.value('higgsIsTauTau'.join(mcColl), min=1),
            steps.gen.wDecay(),
            steps.gen.tauDecay(0),
            steps.gen.tauDecay(1),
            ssh.multiplicity('SignalLeptonIndices'.join(mcColl)),
            ssh.pt    ('genP4',100, 0., 250*GeV, hi, xtitle='H_{truth}'),
            ssh.absEta('genP4',100, 0.,       5, hi, xtitle='H_{truth}'),
            ssh.pt    ('genP4',100, 0., 250*GeV, wi, xtitle='W_{truth}'),
            ssh.absEta('genP4',100, 0.,       5, wi, xtitle='W_{truth}'),
            ssf.value('wIsHadronic'.join(mcColl), min=1),
            ssh.pt    ('genP4',100, 0., 250*GeV, wci, 0, xtitle='q_{0,truth}'),
            ssh.pt    ('genP4',100, 0., 250*GeV, wci, 1, xtitle='q_{1,truth}'),
            ssh.absEta('genP4',100, 0.,       5, wci, 0, xtitle='q_{0,truth}'),
            ssh.absEta('genP4',100, 0.,       5, wci, 1, xtitle='q_{1,truth}'),
            ]
        return stepsList

    def listOfCalculables(self,config) :
        obj = config['objects']
        lepton = config['lepton']
        ptMin, etaMax = lepton['ptMin'], lepton['etaMax']
        jetPars = config['jetPars']
        wci = 'wChildrenIndices'.join(mcColl)
        listOfCalculables = supy.calculables.zeroArgs(supy.calculables)
        listOfCalculables += [calculables.gen.genIndices(mcColl, [+24,-24],'W')]
        listOfCalculables += [calculables.gen.SignalLeptonIndices(mcColl, 2.7, 20*GeV)]
        listOfCalculables += [calculables.muon.Indices(obj['muon'], ptMin=ptMin),
                              calculables.genjet.genJetP4(),
                              calculables.genjet.genJetIndices(ptMin=jetPars['minPt'],
                                                               etaMax=jetPars['maxEta']),
                              calculables.recjet.recJetIndices(ptMin=jetPars['minPt'],
                                                               etaMax=jetPars['maxEta']),
                              calculables.genjet.UnmatchedJetIndices('recJetP4','recJetIndices'),
                              calculables.gen.UnmatchedGenIndices(wci, 'recJetP4','recJetIndices'),
                              ]
        listOfCalculables += supy.calculables.fromCollections(calculables.gen, [mcColl])
        listOfCalculables += supy.calculables.fromCollections(calculables.muon, [obj["muon"]])
        listOfCalculables += supy.calculables.fromCollections(calculables.recjet, [obj['jet']])

        return listOfCalculables

    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
        exampleDict.add('WH_2Lep_11',
                        '["/tmp/gerbaudo/wA_noslep_WH_2Lep_11/NTUP_SUSY.01176858._000001.root.1"'
                        ',"/tmp/gerbaudo/wA_noslep_WH_2Lep_11/NTUP_SUSY.01176858._000002.root.1"]',
                        xs = 1.140) #pb # 1.1402753294*0.30636*0.3348500000
        exampleDict.add('WH_Htautau_had',
                        '["/afs/cern.ch/user/g/gerbaudo/work/public/wh/checkFilterEff/test1.NTHUP_TRUTH.root"]',
                        xs=1.140)
        exampleDict.add('WH_Htautau_noHad',
                        '["/afs/cern.ch/user/g/gerbaudo/work/public/wh/checkFilterEff/test2.NTHUP_TRUTH.root"]',
                        xs=1.140)
        basedir='/gdata/atlas/gerbaudo/wh/mc12_8TeV.177503.Herwigpp_UEEE3_CTEQ6L1_sM_wA_noslep_notauhad_WH_2Lep_3.merge.NTUP_SUSY.e2149_s1581_s1586_r3658_r3549_p1512'
        basedir='/gdata/atlas/gerbaudo/wh/mc12_8TeV.177503.Herwigpp_UEEE3_CTEQ6L1_sM_wA_noslep_notauhad_WH_2Lep_3.evgen.NTUP_TRUTH'
        exampleDict.add('WH_2Lep_3',
                        'utils.fileListFromDisk(location = "%s/*.root*", isDirectory = False)'%basedir,
                        xs=(2.1906288266*0.30636*0.3280600000)) #pb
        return [exampleDict]

    def listOfSamples(self,config) :
        test = False #True
        nEventsMax= 4 if test else None
        kViolet, kRed = 880, 632 # see Rtypes.h or import ROOT
        return (#supy.samples.specify(names='WH_2Lep_11', color = kViolet, nEventsMax=nEventsMax)
                #supy.samples.specify(names='WH_Htautau_had', color = kViolet, nEventsMax=nEventsMax)
                #+ supy.samples.specify(names='WH_Htautau_noHad', color = kRed, nEventsMax=nEventsMax)
                supy.samples.specify(names='WH_2Lep_3', color = kViolet, nEventsMax=nEventsMax)
                )

    def conclude(self,pars) :
        org = self.organizer(pars)
        org.scale(lumiToUseInAbsenceOfData=20.0)
        supy.plotter(org,
                     pdfFileName = self.pdfFileName(org.tag),
                     doLog = False,
                     blackList = ['lumiHisto','xsHisto','nJobsHisto'],
                     ).plotAll()

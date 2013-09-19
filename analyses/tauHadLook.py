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
            steps.gen.particlePrinter(),
#             steps.gen.higgsDecay(),
#             steps.gen.wDecay(),
#             ssh.multiplicity('SignalLeptonIndices'.join(mcColl)),
#             ssf.value('higgsIsTauTau'.join(mcColl), min=1),
#             steps.gen.wDecay(),
#             steps.gen.tauDecay(0),
#             steps.gen.tauDecay(1),
#             ssh.multiplicity('SignalLeptonIndices'.join(mcColl)),
#             ssh.pt    ('genP4',100, 0., 250*GeV, hi, xtitle='H_{truth}'),
#             ssh.absEta('genP4',100, 0.,       5, hi, xtitle='H_{truth}'),
#             ssh.pt    ('genP4',100, 0., 250*GeV, wi, xtitle='W_{truth}'),
#             ssh.absEta('genP4',100, 0.,       5, wi, xtitle='W_{truth}'),
#             ssf.value('wIsHadronic'.join(mcColl), min=1),
#             ssh.pt    ('genP4',100, 0., 250*GeV, wci, 0, xtitle='q_{0,truth}'),
#             ssh.pt    ('genP4',100, 0., 250*GeV, wci, 1, xtitle='q_{1,truth}'),
#             ssh.absEta('genP4',100, 0.,       5, wci, 0, xtitle='q_{0,truth}'),
#             ssh.absEta('genP4',100, 0.,       5, wci, 1, xtitle='q_{1,truth}'),
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
        basedir='/gdata/atlas/gerbaudo/wh/borgeSamples/user.gjelsten.slha2mc_DGnoSL_TB10_v1_DGnoSL_TB10_M1M2MU_050_120_160.merge.NTUP_TRUTH..v1/'
        exampleDict.add('M1M2MU_050_120_160',
                        'utils.fileListFromDisk(location = "%s/*.root*", isDirectory = False)'%basedir,
                        xs=(2.1906288266*0.30636*0.3280600000)) #pb
        return [exampleDict]

    def listOfSamples(self,config) :
        test = True #False
        nEventsMax= 4 if test else None
        kViolet, kRed = 880, 632 # see Rtypes.h or import ROOT
        return (supy.samples.specify(names='M1M2MU_050_120_160', color = kViolet, nEventsMax=nEventsMax)
                )

    def conclude(self,pars) :
        org = self.organizer(pars)
        org.scale(lumiToUseInAbsenceOfData=20.0)
        supy.plotter(org,
                     pdfFileName = self.pdfFileName(org.tag),
                     doLog = False,
                     blackList = ['lumiHisto','xsHisto','nJobsHisto'],
                     ).plotAll()

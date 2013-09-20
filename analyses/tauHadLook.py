#!/usr/bin/env python

# Look at the selection efficiency for 2 high-pt leptons and 1(2?) jets
#
# davide.gerbaudo@gmail.com
# 2013-09-18

import supy
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
                        xs=(1.0)) #pb
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

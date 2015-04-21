# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:00:08 2015

@author: georg
"""
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import scipy as sp

class Traces_Visualizer_Stimsorted_Widget(QtGui.QWidget):
    """ plots the current traces, trial sorted with avg 
    2 do: speed issues, maybe disable other trace updater?
    implement in main window?
    implement stim region    
    """
    def __init__(self,Main,parent):
        super(Traces_Visualizer_Stimsorted_Widget, self).__init__()
    
        self.Data_Display = parent
        self.Main = Main
        
        self.plotItems = []
#        self.plotWidgets = []
        self.traces = []
        self.stim_regions = []
        self.vlines = []
        
        self.init_UI()

    def init_UI(self):
        self.plotWidget = pg.GraphicsLayoutWidget(self)
        self.Layout = QtGui.QHBoxLayout(self)
        self.Layout.setMargin(0)
        self.Layout.setSpacing(0)
        self.setLayout(self.Layout)
        pass
    
    def init_data(self):
        # some preparations
        self.trial_labels = self.Main.Data.Metadata.trial_labels
        self.trial_indices = range(self.Main.Data.nTrials)
        self.trial_labels_unique = sp.unique(self.trial_labels)
        self.nStimClasses = len(self.trial_labels_unique)
        self.nRepetitions = self.trial_labels.count(self.trial_labels[0]) # FIXME: this imposes a fixed number of repetitions per trial. this should be changed into a vector holding values for each stim

        # generating the UI
        # looping over StimClasses
        for i,StimClass in enumerate(range(self.nStimClasses)):
            if self.Main.Options.view['trial_labels_on_traces_vis']:
                print self.Main.Options.view['trial_labels_on_traces_vis']
                print "in here???"
                plot = self.plotWidget.addPlot(title=self.trial_labels_unique[StimClass])
            else:
                plot = self.plotWidget.addPlot(title=None) # for inheriting from QWidget
            plot.setLabel('left','F')
            plot.setLabel('bottom','frame #')
            plot.showGrid(x=True,y=True,alpha=0.5)
            
            # link for common axes
            if i != 0:
                plot.setYLink(self.plotItems[0])
                plot.setXLink(self.plotItems[0])
                
            # add the stimulus time marker
            stim_region = pg.LinearRegionItem(values=[self.Main.Options.preprocessing['stimulus_onset'],self.Main.Options.preprocessing['stimulus_offset']],movable=False,brush=pg.mkBrush([50,50,50,100]))
            for line in stim_region.lines:
                line.hide()
            stim_region.setZValue(-1000)
            plot.addItem(stim_region)
            self.stim_regions.append(stim_region)
                
            # add the plot to the list of plots
            self.plotItems.append(plot)
#            self.plotWidgets.append(self.plotWidget)


        for trial in self.trial_indices:
            # draw the trace in the correct panel
            stimClass = self.trial_labels[trial]
            correct_panel_index = sp.where(self.trial_labels_unique == stimClass)[0]
            
            # with the correct pen
            pen = pg.mkPen(self.Main.Options.view['colors'][trial],width=2)

            self.traces.append(self.plotItems[correct_panel_index].plot(pen=pen))
                                        
        # set the layout
        self.Layout.addWidget(self.plotWidget)

        
    def update_display_settings(self):
        """ this is handled via signal/slot mechanism"""
        if (self.Main.ROIs.nROIs > 0 and self.Main.Options.ROI['active_ROI_id'] != None):
            active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
            Traces = self.get_traces()
            
            for trace in self.traces:
                trace.hide()
                
            for n,ind in enumerate(active_inds):
                    self.traces[ind].setData(Traces[:,n])
                    self.traces[ind].show()
            
        for i,StimClass in enumerate(range(self.nStimClasses)):
            if self.Main.Options.view['trial_labels_on_traces_vis']:
                self.plotItems[i].setTitle(self.trial_labels_unique[StimClass])
            else:
                self.plotItems[i].setTitle(None)
        
                    
        # update stim marker
        for stim_region in self.stim_regions:
            stim_region.setRegion([self.Main.Options.preprocessing['stimulus_onset'], self.Main.Options.preprocessing['stimulus_offset']])
    
        # plot labels
#        if self.Main.Options.view['show_dFF'] == True:
#            self.plotItem.setLabel('left','dF/F')
#            
#        if self.Main.Options.view['show_dFF'] == False:
#            self.plotItem.setLabel('left','F [au]')
#        
#        pass
    def get_traces(self):
        """ helper for calculating the traces matrix """
        active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
                
        # implementation using the pyqtgraph internal slicing
        ROI = self.Main.ROIs.ROI_list[self.Main.Options.ROI['active_ROI_id']]
        
        # func bool mask slicing
        mask, inds = self.Main.ROIs.get_ROI_mask(ROI)  ### FIXME signal needed?
        
        if self.Main.Options.view['show_dFF']:
            sliced = self.Main.Data.dFF[mask,:,:][:,:,active_inds]
        else:
            sliced = self.Main.Data.raw[mask,:,:][:,:,active_inds]

        Traces = sp.average(sliced,axis=0)
        
        return Traces
        
    def update_traces(self):

        if (self.Main.ROIs.nROIs > 0 and self.Main.Options.ROI['active_ROI_id'] != None):
            active_inds = sp.where(self.Main.Options.view['show_flags'])[0]
            Traces = self.get_traces()

            for n,ind in enumerate(active_inds):
                self.traces[ind].setData(Traces[:,n])

    def reset(self):
        for trace in self.traces:
            trace.clear()
        self.traces = []
        
        pass
    
    
if __name__ == '__main__':
    import Main
    Main.main()
    pass
import logging
import numpy as np
import pandas as pd
from datetime import datetime, time
from xarray import open_dataset

from mosart.reservoirs.reservoirs import initialize_reservoir_state

def initialize_state(self):

    # restart file
    if self.config.get('simulation.restart_file') is not None and self.config.get('simulation.restart_file') != '':
        logging.info('Loading restart file.')
        self.restart = open_dataset(self.config.get('simulation.restart_file'))
        # TODO set current timestep based on restart
        # TODO initialize state from restart file
        logging.error('Restart file not yet implemented. Aborting.')
        raise NotImplementedError

    # initialize all the state variables
    logging.info('Initializing state variables.')

    # current timestep
    self.current_time = datetime.combine(self.config.get('simulation.start_date'), time.min)

    # initialize state variables
    logging.debug(' - variables')
    state_dataframe = None
    for var in [
        # flow [m3/s]
        # flow
        'flow',
        # outflow into downstream links from previous timestep [m3/s]
        # eroup_lagi
        'outflow_downstream_previous_timestep',
        # outflow into downstream links from current timestep [m3/s]
        # eroup_lagf
        'outflow_downstream_current_timestep',
        # initial outflow before dam regulation at current timestep [m3/s]
        # erowm_regi
        'outflow_before_regulation',
        # final outflow after dam regulation at current timestep [m3/s]
        # erowm_regf
        'outflow_after_regulation',
        # outflow sum of upstream gridcells, average [m3/s]
        # eroutUp_avg
        'outflow_sum_upstream_average',
        # lateral flow from hillslope, including surface and subsurface runoff generation components, average [m3/s]
        # erlat_avg
        'lateral_flow_hillslope_average',
        # routing storage [m3]
        # volr
        'storage',
        # routing change in storage [m3/s]
        # dvolrdt
        'delta_storage',
        # routing change in storage masked for land [m3/s]
        # dvolrdtlnd
        'delta_storage_land',
        # routing change in storage masked for ocean [m3/s]
        # dvolrdtocn
        'delta_storage_ocean',
        # basin derived flow [m3/s]
        # runoff
        'runoff',
        # return direct flow [m3/s]
        # runofftot
        'runoff_total',
        # runoff masked for land [m3/s]
        # runofflnd
        'runoff_land',
        # runoff masked for ocean [m3/s]
        # runoffocn
        'runoff_ocean',
        # direct flow [m3/s]
        # direct
        'direct',
        # direct-to-ocean forcing [m3/s]
        # qdto
        'direct_to_ocean',
        # flood water [m3/s]
        # flood
        'flood',
        # hillslope surface water storage [m]
        # wh
        'hillslope_storage',
        # change of hillslope water storage [m/s]
        # dwh
        'hillslope_delta_storage',
        # depth of hillslope surface water [m]
        # yh
        'hillslope_depth',
        # surface runoff from hillslope [m/s]
        # qsur
        'hillslope_surface_runoff',
        # subsurface runoff from hillslope [m/s]
        # qsub
        'hillslope_subsurface_runoff',
        # runoff from glacier, wetlands, and lakes [m/s]
        # qgwl
        'hillslope_wetland_runoff',
        # overland flor from hillslope into subchannel (outflow is negative) [m/s]
        # ehout
        'hillslope_overland_flow',
        # subnetwork water storage [m3]
        # wt
        'subnetwork_storage',
        # subnetwork water storage at previous timestep [m3]
        # wt_last
        'subnetwork_storage_previous_timestep',
        # change of subnetwork water storage [m3]
        # dwt
        'subnetwork_delta_storage',
        # depth of subnetwork water [m]
        # yt
        'subnetwork_depth',
        # cross section area of subnetwork [m2]
        # mt
        'subnetwork_cross_section_area',
        # hydraulic radii of subnetwork [m]
        # rt
        'subnetwork_hydraulic_radii',
        # wetness perimeter of subnetwork [m]
        # pt
        'subnetwork_wetness_perimeter',
        # subnetwork flow velocity [m/s]
        # vt
        'subnetwork_flow_velocity',
        # subnetwork mean travel time of water within travel [s]
        # tt
        'subnetwork_mean_travel_time',
        # subnetwork evaporation [m/s]
        # tevap
        'subnetwork_evaporation',
        # subnetwork lateral inflow from hillslope [m3/s]
        # etin
        'subnetwork_lateral_inflow',
        # subnetwork discharge into main channel (outflow is negative) [m3/s]
        # etout
        'subnetwork_discharge',
        # main channel storage [m3]
        # wr
        'channel_storage',
        # change in main channel storage [m3]
        # dwr
        'channel_delta_storage',
        # main channel storage at last timestep [m3]
        # wr_last
        'channel_storage_previous_timestep',
        # main channel water depth [m]
        # yr
        'channel_depth',
        # cross section area of main channel [m2]
        # mr
        'channel_cross_section_area',
        # hydraulic radii of main channel [m]
        # rr
        'channel_hydraulic_radii',
        # wetness perimeter of main channel[m]
        # pr
        'channel_wetness_perimeter',
        # main channel flow velocity [m/s]
        # vr
        'channel_flow_velocity',
        # main channel evaporation [m/s]
        # erlg
        'channel_evaporation',
        # lateral flow from hillslope [m3/s]
        # erlateral
        'channel_lateral_flow_hillslope',
        # inflow from upstream links [m3/s]
        # erin
        'channel_inflow_upstream',
        # outflow into downstream links [m3/s]
        # erout
        'channel_outflow_downstream',
        # outflow into downstream links from previous timestep [m3/s]
        # TRunoff%eroup_lagi
        'channel_outflow_downstream_previous_timestep',
        # outflow into downstream links from current timestep [m3/s]
        # TRunoff%eroup_lagf
        'channel_outflow_downstream_current_timestep',
        # initial outflow before dam regulation at current timestep [m3/s]
        # TRunoff%erowm_regi
        'channel_outflow_before_regulation',
        # final outflow after dam regulation at current timestep [m3/s]
        # TRunoff%erowm_regf
        'channel_outflow_after_regulation',
        # outflow sum of upstream gridcells, instantaneous [m3/s]
        # eroutUp
        'channel_outflow_sum_upstream_instant',
        # outflow sum of upstream gridcells, average [m3/s]
        # TRunoff%eroutUp_avg
        'channel_outflow_sum_upstream_average',
        # lateral flow from hillslope, including surface and subsurface runoff generation components, average [m3/s]
        # TRunoff%erlat_avg
        'channel_lateral_flow_hillslope_average',
        # flux for adjustment of water balance residual in glacier, wetlands, and lakes [m3/s]
        # ergwl
        'channel_wetland_flux',
        # streamflow from outlet, positive is out [m3/s]
        # flow
        'channel_flow',
        # a column of always all zeros, to use as a utility
        'zeros'
    ]:
        if state_dataframe is not None:
            state_dataframe = state_dataframe.join(pd.DataFrame(np.zeros(self.get_grid_size()), columns=[var]))
        else:
            state_dataframe = pd.DataFrame(np.zeros(self.get_grid_size()), columns=[var])
    
    # tracers
    # TODO how to handle ice?
    state_dataframe = state_dataframe.join(pd.DataFrame(
        np.full(self.get_grid_size(), self.parameters.LIQUID_TRACER), columns=['tracer']
    ))

    # mask on whether or not to perform euler calculations
    state_dataframe = state_dataframe.join(pd.DataFrame(np.where(
        np.array(state_dataframe.tracer.eq(self.parameters.LIQUID_TRACER)),
        True,
        False
    ), columns=['euler_mask']))
    
    # add the state to self
    self.state = state_dataframe
    
    if self.config.get('water_management.enabled', False):
        logging.debug(' - reservoirs')
        initialize_reservoir_state(self)
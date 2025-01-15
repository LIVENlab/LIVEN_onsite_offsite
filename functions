import bw2io as bi
import bw2data as bd
import pandas as pd
import warnings
import sys

# all the activities that either produce direct emissions on-site during installation, use, maintenance and
# end-of-life, or are considered part of an infrastructure. Example of the latest: the 'inverter' and 'photovoltaic
# panel' are inputs of the 'photovoltaic power plant'.
AUX_ACTS = ['excavation, hydraulic digger',
            'excavation, skid-steer loader',
            'road',
            'diesel, burned in building machine',
            'diesel, burned in diesel-electric generating set, 10MW',
            'diesel, burned in diesel-electric generating set, 18.5kW',
            'sewer grid construction',
            'photovoltaic mounting system',  # photovoltaics
            'photovoltaic panel,',  # photovoltaics
            'photovoltaic panel production',  # photovoltaics
            'photovoltaics, electric installation',  # photovoltaics
            'inverter',  # photovoltaics
            'solar tower power plant, 20 MW',  # solar tower
            'building, hall, wood construction',  # solar tower
            'air input/output unit',  # biogas
            'catalytic converter, three-way, 19.1l',  # biogas
            'catalytic converter production, three-way, 19.1l',  # biogas
            'gas motor, 206kW',  # biogas
            'gas motor production, 206kW',  # biogas
            '160kW electrical',  # biogas
            '200kW electrical',  # biogas
            'deep well',  # geothermal
            '6.4MWth',  # geothermal
            'waste reinforced concrete',
            'waste brick',
            'waste cement in concrete and mortar',
            'waste cement-fibre slab',
            'waste concrete gravel',
            'waste concrete, not reinforced',
            'waste gypsum plasterboard',
            'waste mineral plaster',
            'waste mineral wool',
            'waste reinforcement steel']

# names of the infrastructure contained inside the 'electricity production' datasets. Example: 'wind turbine, 800kW,
# moving part' is an input of the 'electricity production, wind, onshore, <1 MW'
TECHNOLOGY_NAMES = ['power plant', 'photovoltaic', 'turbine', 'co-generation unit', 'network connection']


def explore_tiers(max_tier, act):
    """
    Explores all tiers without any filters.
    :param max_tier: until which tier you want to explore (considering the first one to be 0).
    :param act: selected activity from a database. Example: bd.Database('database_name').get(code='code').
    :return: dictionary with the following structure (where tier_0 and tier_1 are integers, act is an activity and
                exchange_1 is the activity corresponding to the exchange):
    full_tier_dict = {tier_0: {act: [exchange_1, exchange_2, exchange_3]},
                        tier_1: {act_1: [exchange_1, exchange_2, exchange_3], act_2: [exchange_1, exchange_2]}}
    """
    # full_tier_dict = structure of the final dictionary
    # tech = dictionary with the following structure -> {act: [exchange_1, exchange_2, exchange_3]}
    # tech_name_tier = list containing the activities of the technosphere exchanges -> [exchange_1, exchange_2, exchange_3]
    full_tier_dict = {}
    tier = 0
    while tier < max_tier:
        tech = {}
        # for the first tier (tier == 0)
        if len(full_tier_dict.keys()) == 0:
            tech_name_tier = [ex.input for ex in act.technosphere()]
            tech[act] = tech_name_tier
            full_tier_dict[tier] = tech
        # for all the tiers but the first (tier > 0)
        else:
            last_values = list(list(full_tier_dict.values())[-1].values())
            for value in last_values:
                for t in value:
                    tech_name_tier = [ex.input for ex in t.technosphere()]
                    tech[t] = tech_name_tier
                full_tier_dict[tier] = tech
        tier += 1
    return full_tier_dict


def explore_tiers_filtered(max_tier, activity):
    """
    Explores all tiers with certain filters. In general, we want to explore the tiers only for those elements
    included in AUX_ACTS.
    :param max_tier: until which tier you want to explore (considering the first one to be 0).
    :param activity: selected activity from a database. Example: bd.Database('database_name').get(code='code').
    :return: dictionary with the following structure (where tier_0 and tier_1 are integers, act is an activity and
                exchange_1 is the activity corresponding to the exchange):
    full_tier_dict = {tier_0: {act: [exchange_1, exchange_2, exchange_3]},
                        tier_1: {act_1: [exchange_1, exchange_2, exchange_3], act_2: [exchange_1, exchange_2]}}
    """
    # full_tier_dict = structure of the final dictionary
    # tech = dictionary with the following structure -> {act: [exchange_1, exchange_2, exchange_3]}
    # tech_name_tier = list containing the activities of the technosphere exchanges -> [exchange_1, exchange_2, exchange_3]
    tier_dict = {}
    tier = 0
    power_plant = False
    next_tier = False
    wastewater = False
    while tier < max_tier:
        tech = {}

        # we need the variable next_tier to make sure that we only start filtering for the elements in aux_acts when
        # we are on the next tier. Otherwise, if we have two infrastructure elements in the same tier,
        # we would escape the second one.
        if power_plant:
            next_tier = True
        # solve the first tier filtering for only transportation and infrastructure activities
        if len(tier_dict.keys()) == 0:
            # only include transport (unit = 'ton kilometer'), infrastructure (unit = unit) activities or diesel use
            # (name includes 'diesel')
            tech_name_tier = [ex.input for ex in activity.technosphere() if
                              'unit' in ex.unit or 'ton kilometer' in ex.unit or 'diesel' in ex.input._data[
                                  'name'] or 'wastewater' in ex.input._data['name']]
            # code for those cases (e.g. co-generation) where there is no market activity for the infrastructure but
            # directly the 'construction' activity. Also, to include in an appropriate way those cases (e.g. pv open
            # ground) where there is a sewer grid construction, but we want to avoid the inclusion of the wastewater
            # treatment (not on-site)
            for pow_unit in tech_name_tier:
                if 'construction' in pow_unit._data['name'] and 'This is a market activity' not in pow_unit._data[
                    'comment']:
                    power_plant = True
                #if 'wastewater' in pow_unit._data['name']:
                    #wastewater = True
            # tech: key = activity, value = list of technosphere exchanges
            tech[activity] = tech_name_tier
            # add the 'tech' dictionary as a value of its tier to the 'tier_dict' general dictionary
            tier_dict[tier] = tech
        # solve every other tiers but the first one (tier > 0)
        else:
            # last_values = list of lists that stores all the activities from the previous tier that have to be explored
            # in this tier
            last_values = list(list(tier_dict.values())[-1].values())
            for value in last_values:
                for t in value:
                    # don't explore the transport activities (if they are not markets)
                    if 'transport' in t._data['name'] and 'This is a market activity' not in t._data['comment']:
                        pass
                    # once we found the infrastructure elements (power_plant = True) and we are on the next tier (
                    # next_tier = True), we want to filter by 'aux_acts' activities only. An extra filtering step for
                    # the waste activities is applied, to avoid including the 'sorting plant and 'recycling' and only
                    # consider the 'collection for final disposal', which is the only one happening on-site.
                    elif power_plant and next_tier:
                        tech_name_tier = [ex.input for ex in t.technosphere() if
                                          any(name in ex.input._data['name'] for name in AUX_ACTS) and not any(
                                              n in ex.input._data['name'] for n in [', sorting plant', ', recycling'])]
                        tech[t] = tech_name_tier
                    #elif wastewater:
                        #tech_name_tier = [ex.input for ex in t.technosphere() if
                        #                  'treatment of wastewater' not in ex.input._data['name']]
                        #tech[t] = tech_name_tier
                        #for te in tech_name_tier:
                        #    if any(name in te._data['name'] for name in
                        #           TECHNOLOGY_NAMES) and 'This is a market activity' not in te._data['comment']:
                        #        power_plant = True
                    # if we have not found the infrastructure yet, we consider all the elements in the tier.
                    else:
                        tech_name_tier = [ex.input for ex in t.technosphere()]
                        tech[t] = tech_name_tier
                        # check if the exchanges of the activity are infrastructure activities or not (markets excluded).
                        for te in tech_name_tier:
                            if any(name in te._data['name'] for name in
                                   TECHNOLOGY_NAMES) and 'This is a market activity' not in te._data['comment']:
                                power_plant = True
            tier_dict[tier] = tech
        tier += 1
    return tier_dict


def pniec_technologies(tier: int, database: str):
    """
    Filter all the technologies included in PNIEC and obtain a dictionary for each of them, first, and finally a list
    of all the dictionaries.
    :param tier: until what tier should we explore pniec technologies?
    :param database: in what database should we search the activities from pniec?
    :return: tier_dict_list. A list of dictionaries.
    """
    # pumped storage
    tier_dict_pumped = explore_tiers_filtered(tier,
                                            activity=bd.Database(database).get(code="efae6a026882b2111c41f39db1d9fb13"))
    # hard coal
    tier_dict_coal = explore_tiers_filtered(tier,
                                            activity=bd.Database(database).get(code="cfa79d34d94d122a4fd35786da2c6d4e"))
    # lignite
    tier_dict_lign = explore_tiers_filtered(tier,
                                            activity=bd.Database(database).get(code="068842db6eef205f8d27b326e7e55a0c"))
    # wind, onshore, <1MW
    tier_dict_wind_on_less1 = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="72cc067e1f4093c2e4c6ac9bdc93d844"))
    # wind, onshore, 1-3MW
    tier_dict_wind_on_1_3 = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="ed3da88fc23311ee183e9ffd376de89b"))
    # wind, onshore, >3MW
    tier_dict_wind_on_more3 = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="0d48975a3766c13e68cedeb6c24f6f74"))
    # wind, offshore, 1-3MW
    tier_dict_wind_off = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="6ebfe52dc3ef5b4d35bb603b03559023"))
    # photovoltaic, openground
    tier_dict_pv_op = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="46ec4bc016881dafa23a3bbc4c11a7e4"))
    # photovoltaic, slanted-roof, single
    tier_dict_pv_single = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="8b0ca7f94a5fc4975be65b4026151bc0"))
    # photovoltaic, slanted-roof, multi
    tier_dict_pv_multi = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="0a078df4dbe9c2322131b4413547c0ae"))
    # solar tower
    tier_dict_solar_tower = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="f2700b2ffcb6b32143a6f95d9cca1721"))
    # solar parabolic
    tier_dict_solar_parabolic = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="19040cdacdbf038e2f6ad59814f7a9ed"))
    # natural gas, combined cycle power plant
    tier_dict_combined = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="fb2cd8e31788cb9a241255b25cddf56d"))
    # oil
    tier_dict_oil = explore_tiers_filtered(tier,
                                           activity=bd.Database(database).get(code="8512aa7eb21d45b94590bb09716506b8"))
    # nuclear, boiling water reactor
    tier_dict_bwr = explore_tiers_filtered(tier,
                                           activity=bd.Database(database).get(code="0919171fc84f3dd3ed892700571f313b"))
    # nuclear, pressure water reactor
    tier_dict_pwr = explore_tiers_filtered(tier,
                                           activity=bd.Database(database).get(code="3962c6614a68a912b1236ea45db763e7"))
    # hydro, reservoir, non-alpine region
    tier_dict_hydro_res = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="3021d25fd47ef22859c41df46d489a14"))
    # hydro, run-of-river
    tier_dict_hydro_run = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="3f9af15db6e86e39021de2d013bf26d3"))
    # co-generation, wood chips
    tier_dict_co_wood = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="cc7b47e491ad9fc3bda416c2571e741c"))
    # cogen, nat gas
    tier_dict_co_nat = explore_tiers_filtered(tier, activity=bd.Database(database).get(
        code="9c5387df72e4d6bde29bfbd7cf2646d5"))


    # deep geothermal
    #tier_dict_geo = explore_tiers_filtered(tier,
    #                                       activity=bd.Database(database).get(code="2bcb8eee2acf49a326f2de20929e6fc8"))

    # co-generation, biogas
    #tier_dict_biogas = explore_tiers_filtered(tier, activity=bd.Database(database).get(
    #    code="4de25bf8baf97e6cdaf2b4d4721a71a4"))
    # co-generation, hard coal
    #tier_dict_co_coal = explore_tiers_filtered(tier, activity=bd.Database(database).get(
    #    code="4808a32c75e7aee814441cf3f711ba69"))
    # co-generation, natural gas
    #tier_dict_co_gas = explore_tiers_filtered(tier, activity=bd.Database(database).get(
    #    code="458056dfee83e9df02528e8f6578cc3a"))
    # co-generation, oil
    #tier_dict_co_oil = explore_tiers_filtered(tier, activity=bd.Database(database).get(
    #    code="e084d924262e8dd033e90b2b99c944b2"))

    tier_dict_list = [tier_dict_wind_on_1_3, tier_dict_wind_on_less1, tier_dict_pv_single, tier_dict_pwr,
                      tier_dict_pv_multi, tier_dict_wind_off, tier_dict_solar_tower, tier_dict_coal,
                      tier_dict_hydro_res, tier_dict_co_nat, tier_dict_solar_parabolic,
                      tier_dict_lign, tier_dict_oil, tier_dict_hydro_run, tier_dict_pv_op,
                      tier_dict_co_wood, tier_dict_combined, tier_dict_pumped,
                      tier_dict_wind_on_more3, tier_dict_bwr]
    return tier_dict_list


def get_unique(tier_dict_list=None, pniec=False, pniec_tier=None, database=None):
    """
    Obtain a list with all single activities contained in tier_dict_list (which is a list of dictionaries, each of them
    containing the filtered tiers of electricity production technology datasets). This tier_dict_list can be
    tailor-made with different electricity production technologies, or it can come from running pniec_technologies().
    In the later case, pniec variable must be set to True.
    :param tier_dict_list: we must give a list of tier_dicts in case pniec is False.
    :param pniec: if it is True, it means we are analysing all technologies contained in pniec
    :param pniec_tier: until what tier should we explore pniec technologies?
    :param database: in what database should we search the activities from pniec?
    :return: unique_list. A list of all the single activities contained in all the tiers explored.
    """
    empty_list = []
    if pniec:
        tier_dict_list = pniec_technologies(pniec_tier, database)
    for a in tier_dict_list:
        for key in a.keys():
            if key == 0:
                value = a[key].keys()
                for v in value:
                    empty_list.append(v)
                for e in a[key][v]:
                    empty_list.append(e)
            else:
                value = a[key].keys()
                for v in value:
                    for e in a[key][v]:
                        empty_list.append(e)
    unique_list = list(set(empty_list))
    return unique_list


def create_activities_copy(output_database: str, tier_dict_list=None, pniec=False, pniec_tier=None, database=None):
    """
    From the single activities obtained by running get_unique(), create a copy on a new database called output_database.
    :param output_database: string. What database should the activities be copied to?
    :param tier_dict_list: we must give a list of tier_dicts in case pniec is False.
    :param pniec: if it is True, it means we are analysing all technologies contained in pniec
    :param pniec_tier: until what tier should we explore pniec technologies?
    :param database: in what database should we search the activities from pniec?
    :return:
    """
    if output_database not in bd.databases:
        new_db = bd.Database(output_database)
        new_db.register()
    unique_list = get_unique(tier_dict_list, pniec, pniec_tier, database)
    for act in unique_list:
        act.copy(database=output_database)


def export_database(database: str):
    """
    Export the database created and filled with activities by running create_activities_copy().
    NOTE: in my case the output is automathically saved in: Users -> 1361185 -> AppData -> Local -> pylca -> Brightway3
    :param database: string. What database should be exported?
    """
    bi.export.write_lci_excel(database)


def solve_excel_issues(input_path: str, output_path: str):
    """
    The exported database on Excel format from brightway (export_database()) has an issue. For every activity, it
    gives two 'activity' fields, the first one with the name of the activity, and the second one with a kind of code.
    If you import that Excel, it gives issues. Therefore, it is necessary to remove the 'activity' that is related to
    the code. This is exactly what this code does (in a very rudimentary way).
    IMPORTANT before running. Add a first row with index 'A' on the first column.
    IMPORTANT before running. Change the db name on the Excel to not overwrite 'new_db' once you import it.
    IMPORTANT after running. Delete first row.
    :param input_path: input path to the database Excel file exported from brightway.
    :param output_path: output path where the fixed Excel should be saved.
    """
    # Step 1: Read the Excel file into a pandas dataframe
    df = pd.read_excel(input_path)

    # Step 2: Find rows with 'Activity' in column A and remove the next row
    to_remove = []
    for idx, val in df['A'].items():
        if val == 'Activity':
            to_remove.append(idx + 1)
    df.drop(to_remove, inplace=True, errors='ignore')

    # Step 3: Save the modified dataframe to a new Excel file
    df.to_excel(output_path, index=False)


def import_excel(file_path: str):
    """
    Imports an Excel database, links it internally and writes it in brightway.
    IMPORTANT: make sure to have removed the first row of the file_path in case it is 'A'.
    :param file_path: path to the output file of solve_excel_issues.
    :return:
    """
    excel = bi.ExcelImporter(file_path)
    # link database internally
    excel.match_database(fields=('name', 'unit', 'location'))
    # link database exchanges with the biosphere
    excel.apply_strategies()
    # remove unlinked exchanges
    excel.drop_unlinked(True)
    # write database
    excel.write_database()


def export_solved_inventory(activity, method, out_path):
    """
    All credits to Ben Portner.
    :param activity:
    :param method:
    :param out_path:
    :return:
    """
    lca = activity.lca(method, 1)
    lca.lci()
    cutoff = None
    array = lca.inventory.sum(axis=1)
    if cutoff is not None and not (0 < cutoff < 1):
        warnings.warn(f"Ignoring invalid cutoff value {cutoff}")
        cutoff = None
    total = array.sum()
    include = lambda x: abs(x / total) >= cutoff if cutoff is not None else True
    if hasattr(lca, 'dicts'):
        mapping = lca.dicts.biosphere
    else:
        mapping = lca.biosphere_dict
    data = []
    for key, row in mapping.items():
        amount = array[row, 0]
        if include(amount):
            data.append((bd.get_activity(key), row, amount))
    data.sort(key=lambda x: abs(x[2]))
    df = pd.DataFrame([{
        'row_index': row,
        'amount': amount,
        'name': flow.get('name'),
        'unit': flow.get('unit'),
        'categories': str(flow.get('categories'))
    } for flow, row, amount in data
    ])
    df.to_excel(out_path)


def change_hydro_activities(imp_db=bd.Database('onsite_complete_db')):
    """
    hydro activities (hydro, run-of-river) and (hydro, reservoir, non-alpine region) have the land use in the
    electricity production inventory instead of in the infrastructure inventory. What we do with this function is to
    relocate those land use biosphere flows (transformation, occupation, and volume occupied) from the electricity
    production inventory to the infrastructure inventory. In addition, the inventory hydro, reservoir, non-alpine region
    does contain a Transformation biosphere flow (Transformation, from unspecified) that does not have a CF in the
    RECIPE land use impact category. Thus, we are changing it for the biosphere flow
    Transformation, from unspecified, natural that does impact in the RECIPE land use impact category.
    """
    try:
        res = imp_db.get(
            '6e99d89131d245489e1c5e9056f89f6e')  # you may need to change the code to get the activity that you wish
        res_elec = imp_db.get(
            'd49a199e8db24dc8a394a28ebed1bb5e')  # you may need to change the code to get the activity that you wish
        run = imp_db.get(
            '5de9882905024b1dad99647f87b37fec')  # you may need to change the code to get the activity that you wish
        run_elec = imp_db.get(
            'a4bb733921774009a2ac8ea5e084aaca')  # you may need to change the code to get the activity that you wish
    except bd.errors.UnknownObject:
        print('Make sure to change the code of "hydro, run-of-river" and "hydro, reservoir, non-alpine region" '
              'activities in the function change_hydro_activities(). Select the appropiate codes from your database "imp_db"')
        sys.exit()

    tec_res_elec = [e for e in res_elec.technosphere()][0].amount
    tec_run_elec = [e for e in run_elec.technosphere()][0].amount
    bio_res_elec = [e for e in res_elec.biosphere()]
    bio_run_elec = [e for e in run_elec.biosphere()]
    res_to_be_changed = []
    for e in bio_res_elec:
        if 'Transformation' in e.input._data['name'] or 'Occupation' in e.input._data['name'] or 'Volume occupied' in \
                e.input._data['name'] or 'Methane' in e.input._data['name'] or 'Carbon dioxide' in e.input._data['name']:
            res_to_be_changed.append(e)
    run_to_be_changed = []
    for e in bio_run_elec:
        if 'Transformation' in e.input._data['name'] or 'Occupation' in e.input._data['name'] or 'Volume occupied' in \
                e.input._data['name'] or 'Methane' in e.input._data['name'] or 'Carbon dioxide' in e.input._data['name']:
            run_to_be_changed.append(e)

    transformation_from_uns_nat = bd.Database('biosphere3').get(
        '1a1d0d4b-6b95-4815-ad06-2ec5fe333c43')  # you may need to change the code to get the activity that you wish
    for e in run_to_be_changed:
        if 'Transformation, from unspecified' in str(e.input):
            print(transformation_from_uns_nat, e.amount / tec_res_elec, e.unit)
            new_exc = run.new_exchange(input=transformation_from_uns_nat, amount=e.amount / tec_run_elec, unit=e.unit,
                                       type='biosphere')
            new_exc.save()
            e.delete()
        else:
            print(e.input, e.amount / tec_res_elec, e.unit)
            new_exc = run.new_exchange(input=e.input, amount=e.amount / tec_run_elec, unit=e.unit, type='biosphere')
            new_exc.save()
            e.delete()
    for e in res_to_be_changed:
        if 'Transformation, from unspecified' in str(e.input):
            print(transformation_from_uns_nat, e.amount / tec_res_elec, e.unit)
            new_exc = res.new_exchange(input=transformation_from_uns_nat, amount=e.amount / tec_res_elec, unit=e.unit,
                                       type='biosphere')
            new_exc.save()
            e.delete()
        else:
            print(e.input, e.amount / tec_res_elec, e.unit)
            new_exc = res.new_exchange(input=e.input, amount=e.amount / tec_res_elec, unit=e.unit, type='biosphere')
            new_exc.save()
            e.delete()

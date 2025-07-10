import functions

############# execute the code for pniec technologies ###################
functions.bd.projects.set_current("pniec_project")

# Load biosphere3 and LCIA Methods
functions.bi.bw2setup()

# import ecoinvent
spold_files = r"C:\ecoinvent_data\3.9.1\cutoff\datasets"
if "cutoff391" not in functions.bd.databases:
    ei = functions.bi.SingleOutputEcospold2Importer(spold_files, "cutoff391", use_mp=False)
    ei.apply_strategies()
    ei.write_database()
cutoff391 = functions.bd.Database("cutoff391")

# create a copy of the entire ecoinvent database
if "my_cutoff391" not in functions.bd.databases:
    cutoff391.copy("my_cutoff391")
my_cutoff39 = functions.bd.Database("my_cutoff391")

# create copies of all the activities explored from the pniec technologies
functions.create_activities_copy(output_database='new_db', pniec=True, pniec_tier=7, database='my_cutoff391')

# export database. NOTE: in my case iy is exported here:
# C:\Users\1361185\AppData\Local\pylca\Brightway3\my_project_bw2_course.150eee5f\output
functions.export_database('new_db')

# fix issues in the Excel
# IMPORTANT before running. Add a first row with index 'A' on the first column.
# IMPORTANT before running. Change the db name on the Excel to not overwrite 'new_db' once you import it.
# IMPORTANT after running. Delete first row.
functions.solve_excel_issues(
    input_path=r'C:\Users\1361185\AppData\Local\pylca\Brightway3\pniec_project.3932fac4\output\lci-new_db.xlsx',
    output_path=r'C:\Users\1361185\AppData\Local\pylca\Brightway3\pniec_project.3932fac4\output\imported_db.xlsx')

# import excel into brightway
functions.import_excel(r'C:\Users\1361185\AppData\Local\pylca\Brightway3\pniec_project.3932fac4\output\imported_db.xlsx')

# delete transport technosphere exchanges (road) and wastewater
imp_db = functions.bd.Database('onsite_complete_db')
transp_act = imp_db.get(code='f327b68bb3c84afc8523344423e87dbb')
act_technosphere = list(transp_act.technosphere())
act_technosphere[0].delete()
act = functions.bd.Database('onsite_complete_db').get('29e10f5bf8c44746a21ee1b822be4f12')
wastewater_consumers = list(act.consumers())
for e in wastewater_consumers:
    e.delete()

# delete biosphere exchanges during the production or manufacturing of the infrastructure
acts_list_unit = [act for act in imp_db if act._data['unit'] == 'unit']

new_dict = {}
for act in acts_list_unit:
    new_dict[act] = list(act.biosphere())

new_dict_2 = {}
for key in acts_list_unit:
    water = False
    hydro = False
    if 'maintenance' not in key._data['name'] and 'construction work' not in key._data['name']:
        for ex in new_dict[key]:
            if 'hydro' in ex.output._data['name']:
                hydro = True
            elif not hydro:
                if 'Water' in ex.input._data['name']:
                    water = True
        if water:
            new_dict_2[key] = list(key.biosphere())

water_list = list(new_dict_2.keys())
for act in water_list:
    act.biosphere().delete()

# modify hydro land transformation and land occupation flows
functions.change_hydro_activities()
# manually delete them in pumped storage (NOTE: need to change code!)
act = imp_db.get('e063055755d14a65ab7414053909f3ce')
ex = [e for e in act.biosphere()
               if 'Transformation' in e.input._data['name'] or 'Occupation' in e.input._data['name']
               or 'Volume occupied' in e.input._data['name'] or 'Methane' in e.input._data['name']
               or 'Carbon dioxide' in e.input._data['name']]
for e in ex:
    e.delete()

# again but in my_cutoff391 (change codes in the function)
functions.change_hydro_activities()
# manually delete them in pumped storage (NOTE: need to change code!)
act = functions.bd.Database('my_cutoff391').get('c6ec353cb0ea4cf8a8bbb9f61237e277')
ex = [e for e in act.biosphere()
               if 'Transformation' in e.input._data['name'] or 'Occupation' in e.input._data['name']
               or 'Volume occupied' in e.input._data['name'] or 'Methane' in e.input._data['name']
               or 'Carbon dioxide' in e.input._data['name']]
for e in ex:
    e.delete()

# create databases
infrastructure_onsite = functions.bd.Database('infrastructure_onsite')
infrastructure_onsite.register()
operation_onsite = functions.bd.Database('operation_onsite')
operation_onsite.register()
infrastructure_total = functions.bd.Database('infrastructure_total')
infrastructure_total.register()
operation_total = functions.bd.Database('operation_total')
operation_total.register()

# copy electricity and heat operation activities to the operation_onsite db
elec_acts = [a for a in imp_db if 'electricity production' in a._data['name'] or 'heat and power' in a._data['name']
             and 'kilowatt hour' in a._data['unit']]
for a in elec_acts:
    a.copy(database='operation_onsite')
# delete the infrastructure
elec_acts_inf = [a for a in operation_onsite if 'electricity production' in a._data['name'] or 'heat and power' in a._data['name']
             and 'kilowatt hour' in a._data['unit']]
for a in elec_acts_inf:
    ex = [e for e in a.technosphere()]
    for e in ex:
        if e.input._data['unit'] == 'unit':
            e.delete()

# copy infrastructure in infrastructure_onsite db
for a in elec_acts:
    ex = [e for e in a.technosphere()]
    for e in ex:
        if e.input._data['unit'] == 'unit':
            e.input.copy(database='infrastructure_onsite')

# copy electricity total from my_cutoff391 to operation_total db
for act in elec_acts:
    name = act._data['name']
    location = act._data['location']
    unit = act._data['unit']
    ref_prod = act._data['reference product']
    c_act = [a for a in functions.bd.Database('my_cutoff391') if a._data['name'] == name and a._data['location'] == location and a._data['unit'] == unit and a._data['reference product'] == ref_prod][0]
    c_act.copy(database='operation_total')
# delete the infrastructure
for a in operation_total:
    ex = [e for e in a.technosphere()]
    for e in ex:
        if e.input._data['unit'] == 'unit':
            e.delete()

# copy infrastructure total from my_cutoff391 to infrastructure_total db
for act in infrastructure_onsite:
    name = act._data['name']
    location = act._data['location']
    unit = act._data['unit']
    ref_prod = act._data['reference product']
    c_act = [a for a in functions.bd.Database('my_cutoff391') if
             a._data['name'] == name and a._data['location'] == location and a._data['unit'] == unit and a._data[
                 'reference product'] == ref_prod][0]
    c_act.copy(database='infrastructure_total')



# calculate LCAs for all databases
methods = [m for m in functions.bd.methods if 'ReCiPe 2016 v1.03, midpoint (H)' in m[0] and 'no LT' not in m[0]]
res_operation_onsite = {}
for a in operation_onsite:
    lca_obj = a.lca(amount=1)
    impacts = {}
    for m in methods:
        lca_obj.switch_method(m)
        lca_obj.lcia()
        impacts[str(m[2])] = lca_obj.score
    res_operation_onsite[str(a._data['name'])] = impacts
res_operation_total = {}
for a in operation_total:
    lca_obj = a.lca(amount=1)
    impacts = {}
    for m in methods:
        lca_obj.switch_method(m)
        lca_obj.lcia()
        impacts[str(m[2])] = lca_obj.score
    res_operation_total[str(a._data['name'])] = impacts
res_infrastructure_total = {}
for a in infrastructure_total:
    lca_obj = a.lca(amount=1)
    impacts = {}
    for m in methods:
        lca_obj.switch_method(m)
        lca_obj.lcia()
        impacts[str(m[2])] = lca_obj.score
    res_infrastructure_total[str(a._data['name'])] = impacts
res_infrastructure_onsite = {}
for a in infrastructure_onsite:
    lca_obj = a.lca(amount=1)
    impacts = {}
    for m in methods:
        lca_obj.switch_method(m)
        lca_obj.lcia()
        impacts[str(m[2])] = lca_obj.score
    res_infrastructure_onsite[str(a._data['name'])] = impacts
df_inf_onsite = functions.pd.DataFrame(res_infrastructure_onsite)
df_inf_total = functions.pd.DataFrame(res_infrastructure_total)
df_op_onsite = functions.pd.DataFrame(res_operation_onsite)
df_op_total = functions.pd.DataFrame(res_operation_total)
df_inf_onsite.to_excel(r'C:\Users\1361185\OneDrive - UAB\PhD_ICTA_Miquel\inventory_disaggregation\pniec_project\v2\infrastructure_onsite.xlsx')
df_inf_total.to_excel(r'C:\Users\1361185\OneDrive - UAB\PhD_ICTA_Miquel\inventory_disaggregation\pniec_project\v2\infrastructure_total.xlsx')
df_op_total.to_excel(r'C:\Users\1361185\OneDrive - UAB\PhD_ICTA_Miquel\inventory_disaggregation\pniec_project\v2\operation_total.xlsx')
df_op_onsite.to_excel(r'C:\Users\1361185\OneDrive - UAB\PhD_ICTA_Miquel\inventory_disaggregation\pniec_project\v2\operation_onsite.xlsx')

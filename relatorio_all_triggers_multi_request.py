from zabbix.api import ZabbixAPI
from json import dumps
import csv

# Create ZabbixAPI class instance
## This line need to be changed *
# zapi = ZabbixAPI(url='', user='', password='')

# Funcoes de coleta
def get_all_items(all_hosts_ids_list):
    hosts_ids_list = all_hosts_ids_list[:]
    items_list = []

    ### Controle de progresso
    qtd_hosts = len(all_hosts_ids_list)
    print("Coletando Items")

    while(len(hosts_ids_list) > 0):
        small_temp_list = []
        if len(hosts_ids_list) < 200:
            for count in range(len(hosts_ids_list)):
                small_temp_list.append(hosts_ids_list.pop())
        else:
            for count in range(200):
                small_temp_list.append(hosts_ids_list.pop())

        ### Controle de progresso
        print("\t-> Progresso:\t"+str(qtd_hosts-len(hosts_ids_list))+"/"+str(qtd_hosts)+" "*30,end="\r")
        ##########

        items = zapi.item.get(output=["itemid","hostid","name","state","key_","status","templateid"],hostids=small_temp_list)

        for item in items:
            items_list.append(item)

    print("")

    return items_list

def get_all_triggers(all_hosts_ids_list):
    hosts_ids_list = all_hosts_ids_list[:]
    triggers_list = []

    ### Controle de progresso
    qtd_hosts = len(all_hosts_ids_list)
    print("Coletando triggers")

    while(len(hosts_ids_list) > 0):

        small_temp_list = []
        if len(hosts_ids_list) < 200:
            for count in range(len(hosts_ids_list)):
                small_temp_list.append(hosts_ids_list.pop())
        else:
            for count in range(200):
                small_temp_list.append(hosts_ids_list.pop())

        ### Controle de progresso
        print("\t-> Progresso:\t"+str(qtd_hosts-len(hosts_ids_list))+"/"+str(qtd_hosts)+" "*30,end="\r")
        ##########

        triggers = zapi.trigger.get(output=["triggerid","description","expression","status","state"],filter={"hostid":small_temp_list},selectFunctions=['itemid'])

        for trigger in triggers:
            triggers_list.append(trigger)

    print("")

    return triggers_list

def zabbix_format_json(hosts, items, triggers):

    ### Controle de progresso
    print("Formatting Data")
    cont = 0
    #########

    for trigger in triggers:
        ### Controle de progresso
        cont += 1
        print("\t-> Formatting Triggers"+"."*(cont//2000),end="\r")
        #########

        ### Formatando atributos das triggers
        trigger["item_ids"] = []

        if trigger["status"] == "0":
            trigger["status"] = "Enabled"
        else:
            trigger["status"] = "Disabled"

        if trigger["state"] == "0":
            trigger["state"] = "up to date"
        else:
            trigger["state"] = "unknown"

        for function in trigger["functions"]:
            trigger["item_ids"].append(function["itemid"])
        ##########

    print("")
    cont = 0

    for item in items:
        ### Controle de progresso
        cont += 1
        print("\t-> Formatting Items"+"."*(cont//500),end="\r")
        #########

        ### Formatando dados dos items
        if item["status"] == "0":
            item["status"] = "Enabled"
        else:
            item["status"] = "Disabled"

        if item["state"] == "0":
            item["state"] = "Normal"
        else:
            item["state"] = "Not supported"
        ##########
        item["triggers"] = []

        for trigger in triggers:
            if item["itemid"] in trigger["item_ids"]:
                item["triggers"].append(trigger)

    print("")
    cont = 0
    for dict_host in hosts:
        cont += 1
        print("\t-> Formatting Hosts"+"."*(cont//500),end="\r")
        ### Alterando estatus do host de numeral para descritivo
        if dict_host["status"] == "0":
            dict_host["status"] = "Enabled"
        else:
            dict_host["status"] = "Disabled"
        ##########

        ### Agregando items no dicionario de hosts
        dict_host["items"] = []
        for item in items:
            if item["hostid"] == dict_host["hostid"]:
                dict_host["items"].append(item)
        ##########

    return hosts

def create_csv_files(hosts):

    ### Controle de progresso
    print("Putting All in a CSV File")

    csv_head_exist = 0
    f_comma = open("AllTriggers_comma.csv",'w')
    f_semicolon = open("AllTriggers_semicolon.csv",'w')


    header = "Host ID,Host,Hostname,Status,Proxy ID,Item ID,Item Name,Item State,Item Status,Key,Template ID,Trigger ID,Description,Expression,Trigger Status,Trigger State\n"
    f_comma.write(header)
    header = "Host ID;Host;Hostname;Status;Proxy ID;Item ID;Item Name;Item State;Item Status;Key;Template ID;Trigger ID;Description;Expression;Trigger Status;Trigger State\n"
    f_semicolon.write(header)

    for host in hosts:
        for item in host["items"]:
            if len(item["triggers"]) > 0:
                for trigger in item["triggers"]:
                    row = host["hostid"]+","+host["host"]+","+host["name"]+","+host["status"]+","+host["proxy_hostid"]+","+item["itemid"]+","+item["name"]+","+item["state"]+","+item["status"]+","+item["key_"]+","+item["templateid"]+","+trigger["triggerid"]+","+trigger["description"]+","+trigger["expression"]+","+trigger["status"]+","+trigger["state"]+"\n"
                    f_comma.write(row)
                    row = host["hostid"]+";"+host["host"]+";"+host["name"]+";"+host["status"]+";"+host["proxy_hostid"]+";"+item["itemid"]+";"+item["name"]+";"+item["state"]+";"+item["status"]+";"+item["key_"]+";"+item["templateid"]+";"+trigger["triggerid"]+";"+trigger["description"]+";"+trigger["expression"]+";"+trigger["status"]+";"+trigger["state"]+"\n"
                    f_semicolon.write(row)
            else:
                row = host["hostid"]+","+host["host"]+","+host["name"]+","+host["status"]+","+host["proxy_hostid"]+","+item["itemid"]+","+item["name"]+","+item["state"]+","+item["status"]+","+item["key_"]+","+item["templateid"]+"\n"
                f_comma.write(row)
                row = host["hostid"]+";"+host["host"]+";"+host["name"]+";"+host["status"]+";"+host["proxy_hostid"]+";"+item["itemid"]+";"+item["name"]+";"+item["state"]+";"+item["status"]+";"+item["key_"]+";"+item["templateid"]+"\n"
                f_semicolon.write(row)


    f_semicolon.close()
    f_comma.close()

### Coletando informações do Zabbix
all_hosts_ids_list = []
hosts_ids = zapi.host.get(output=["hostid"])

for host_id in hosts_ids:
    all_hosts_ids_list.append(host_id["hostid"])

all_items = get_all_items(all_hosts_ids_list)
all_triggers = get_all_triggers(all_hosts_ids_list)
all_hosts = zapi.host.get(output=["hostid","host","name","status","proxy_hostid"])
###########

hosts = zabbix_format_json(all_hosts, all_items, all_triggers)
create_csv_files(hosts)

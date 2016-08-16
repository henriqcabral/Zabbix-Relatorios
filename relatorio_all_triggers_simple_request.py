from zabbix.api import ZabbixAPI
from json import dumps
import csv

# Create ZabbixAPI class instance
# This Line must be changed
## zapi = ZabbixAPI(url='', user='', password='')

hosts = zapi.host.get(output=["hostid","host","name","status","proxy_hostid"])
list_hosts = []

### Controle de progresso
qtd_hosts = len(hosts)
count = 1

print("Coletando informações dos hosts:")

for dict_host in hosts:

    ### Alterando estatus do host de numeral para
    if dict_host["status"] == "0":
        dict_host["status"] = "Enabled"
    else:
        dict_host["status"] = "Disabled"
    ##########

    ### Controle de progresso
    print("Progresso:\t"+str(count)+"/"+str(qtd_hosts)+"("+dict_host["name"]+")"+" "*30,end="\r")
    count += 1
    ##########

    ### Load dos Dicionarios
    dict_host["items"] = zapi.item.get(output=["itemid","state","name","key_","status","templateid"],hostids=dict_host["hostid"])
    triggers = zapi.trigger.get(output=["triggerid","description","expression","status","state"],filter={"hostid":dict_host["hostid"]},selectFunctions=['itemid'])
    ##########

    ### Ajustando dicionario de itens
    for item in dict_host["items"]:
        ### Alterando o Status para descritivo Enabled ou Disabled
        if item["status"] == "0":
            item["status"] = "Enabled"
        else:
            item["status"] = "Disabled"

        if item["state"] == "0":
            item["state"] = "Normal"
        else:
            item["state"] = "Not supported"


        item["triggers"] = []
        for trigger in triggers:

            trigger["expression"] = trigger["expression"].replace(r'\r','').replace("\r", "").replace("\n", "").replace("^M", "")

            for function in trigger["functions"]:
                if function['itemid'] in item["itemid"]:
                    item["triggers"].append(trigger)

    list_hosts.append(dict_host)

print("\nColeta concluida com sucesso!\nIniciando criação do csv:")

csv_head_exist = 0
f_comma = open("ZBXREL_AllTriggers_comma.csv",'w')
f_semicolon = open("ZBXREL_AllTriggers_semicolon.csv",'w')


header = "Host ID,Host,Hostname,Status,Proxy ID,Item ID,Item Name,Item State,Item Status,Key,Template ID,Trigger ID,Trigger Description,Expression,Trigger Status,Trigger State\n"
f_comma.write(header)
header = "Host ID;Host;Hostname;Status;Proxy ID;Item ID;Item Name;Item State;Item Status;Key;Template ID;Trigger ID;Trigger Description;Expression;Trigger Status;Trigger State\n"
f_semicolon.write(header)

for host in list_hosts:
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
print("Processo Concluido!")

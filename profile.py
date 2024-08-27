#!/usr/bin/env python

kube_description = "Phobos Powder profile"
kube_instruction = "To be done"

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.igext as IG

pc = portal.Context()
rspec = PG.Request()

# Profile parameters.
pc.defineParameter("computeNodeCount", "Number of Kubernetes nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("Hardware", "Node Hardware",
                   portal.ParameterType.STRING, "d430", [("d430", "d430"), ("d710", "d710"), ("d820", "d820"), ("pc3000", "pc3000")])
pc.defineParameter("Core", "Core Implementation",
                   portal.ParameterType.STRING, "Open5GS", [("Open5GS", "Open5GS"), ("srsEPC", "srsEPC")])
pc.defineParameter("token", "GitHub Token",
                   portal.ParameterType.STRING, "")
pc.defineParameter("gNBCount", "Number of gNB/eNB nodes",
                   portal.ParameterType.INTEGER, 1)

params = pc.bindParameters()

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

tour = IG.Tour()
tour.Description(IG.Tour.TEXT, kube_description)
tour.Instructions(IG.Tour.MARKDOWN, kube_instruction)
rspec.addTour(tour)

# Network
netmask = "255.255.255.0"
# Backhaul network
backhaul = rspec.Link("Backhaul")
backhaul.link_multiplexing = True
backhaul.vlan_tagging = True
backhaul.best_effort = True

# Midhaul network
midhaul = rspec.Link("Midhaul")
midhaul.link_multiplexing = True
midhaul.vlan_tagging = True
midhaul.best_effort = True

# Fronthaul network
fronthaul = rspec.Link("Fronthaul")
fronthaul.link_multiplexing = True
fronthaul.vlan_tagging = True
fronthaul.best_effort = True

# Core
epc = rspec.RawPC("epc")
epc.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
if params.Core == 'Open5GS':
    epc.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/core/open5gs_setup.sh"))
elif params.Core == 'srsEPC':
    epc.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/core/srsepc_setup.sh"))
epc.hardware_type = params.Hardware
epc.Site('Core')
iface = epc.addInterface()
iface.addAddress(PG.IPv4Address("192.168.1.1", netmask))
backhaul.addInterface(iface)

# Multiple eNB/gNB nodes
for i in range(params.gNBCount):
    enb = rspec.RawPC("enb" + str(i))
    enb.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
    enb.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/ran/enb_setup.sh " + str(i) + " " + str(params.token)))
    enb.hardware_type = params.Hardware
    enb.Site('RAN')

    # Backhaul interface
    iface1 = enb.addInterface()
    iface1.addAddress(PG.IPv4Address("192.168.1." + str(i + 2), netmask))
    backhaul.addInterface(iface1)

    # Midhaul interface
    iface2 = enb.addInterface()
    iface2.addAddress(PG.IPv4Address("192.168.2." + str(i + 1), netmask))
    midhaul.addInterface(iface2)

# Proxy
proxy = rspec.RawPC("proxy")
proxy.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
proxy.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/ran/proxy_setup.sh " + str(params.gNBCount) + " " + str(params.token)))
proxy.hardware_type = params.Hardware
proxy.Site('RAN')
iface = proxy.addInterface()
iface.addAddress(PG.IPv4Address("192.168.2." + str(params.gNBCount + 1), netmask))
midhaul.addInterface(iface)
iface2 = proxy.addInterface()
iface2.addAddress(PG.IPv4Address("192.168.3.1", netmask))
fronthaul.addInterface(iface2)

# K8s Master
kube_m = rspec.RawPC("master")
kube_m.hardware_type = params.Hardware
kube_m.routable_control_ip = True
kube_m.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
kube_m.Site('Kubernetes')
iface = kube_m.addInterface()
iface.addAddress(PG.IPv4Address("192.168.3.2", netmask))
fronthaul.addInterface(iface)
kube_m.addService(PG.Execute(shell="bash", command="/local/repository/scripts/master.sh"))

# Kubernetes Slaves
for i in range(0, params.computeNodeCount):
    kube_s = rspec.RawPC('slave' + str(i))
    kube_s.hardware_type = params.Hardware
    kube_s.routable_control_ip = True
    kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
    kube_s.Site('Kubernetes')
    iface = kube_s.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.3." + str(i + 3), netmask))
    fronthaul.addInterface(iface)
    kube_s.addService(PG.Execute(shell="bash", command="/local/repository/scripts/slave.sh"))

#
# Print and go!
#
pc.printRequestRSpec(rspec)

#!/usr/bin/env python2

import netsnmp
import argparse

def getCAM(DestHost, Version = 2, Community='public'):
  sess = netsnmp.Session(Version = 2, DestHost=DestHost, Community=Community)
  sess.UseLongNames = 1
  sess.UseNumeric = 1 #to have <tags> returned by the 'get' methods untranslated (i.e. dotted-decimal). Best used with UseLongNames

  Vars1 = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.17.4.3.1'))
  result = sess.walk(Vars1)
  #result = sess.getbulk(0, 10, Vars1)#get vars in one req, but dont stop...
  Vars2 = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.17.1.4.1.2'))
  result += sess.walk(Vars2)
  Vars3 = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.31.1.1.1.1'))
  result += sess.walk(Vars3)

  if result == ():
    raise Exception('Error : ' + sess.ErrorStr + '  ' + str(sess.ErrorNum) + '  ' + str(sess.ErrorInd))

  l = {}
  for v in Vars1:
    myid = (v.tag + '.' + v.iid)[24:]
    if v.tag[22] == '1':
      l[myid] = [v.val]
    elif v.tag[22] == '2':
      l[myid] += [v.val]
    elif v.tag[22] == '3':
      l[myid] += [v.val]

  #Get the bridge port to ifIndex mapping, dot1dBasePortIfIndex (.1.3.6.1.2.1.17.1.4.1.2)
  dot1dBasePortIfIndex = {}
  for v in Vars2:
    dot1dBasePortIfIndex[v.iid] = v.val

  for cle, valeur in l.items():
    valeur += [dot1dBasePortIfIndex[valeur[1]]]

  ifName = {}
  for v in Vars3:
    ifName[v.iid] = v.val
  for cle, valeur in l.items():
    valeur += [ifName[valeur[3]]]

  return l


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Describe this program')
  #parser.add_argument('-v', '--version', dest = 'version', type = int, default = 2, help = 'Version of the protocol. Only v2 is implemented at the moment.')
  parser.add_argument('desthost', action = 'store', default = 'localhost', help = 'Address of the switch')
  parser.add_argument('-c', '--community', dest = 'community', action = 'store', default = 'public', help = 'The community string, default is "public".')
  args = parser.parse_args()
  try:
    l = getCAM(Version = 2, DestHost=args.desthost, Community=args.community)
  except Exception as e:
    print(e)
  else:
    for t in l.values():
      print(''.join('%02x:' % ord(b) for b in bytes(t[0]))[:-1] + ' = ' + t[4])

/*
 * net.h
 *
 * Copyright (C) 2007  Red Hat, Inc.  All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef H_LOADER_NET
#define H_LOADER_NET

#include <newt.h>
#include "../isys/iface.h"
#include "loader.h"

#define DHCP_METHOD_STR   _("Dynamic IP configuration (DHCP)")
#define DHCPV6_METHOD_STR _("Dynamic IP configuration (DHCPv6)")
#define MANUAL_METHOD_STR _("Manual configuration")
#define AUTO_METHOD_STR   _("Automatic neighbor discovery")

struct intfconfig_s {
    newtComponent ipv4Entry, cidr4Entry;
    newtComponent ipv6Entry, cidr6Entry;
    newtComponent gwEntry, nsEntry;
    const char *ipv4, *cidr4;
    const char *ipv6, *cidr6;
    const char *gw, *gw6, *ns;
};

struct netconfopts {
    char ipv4Choice;
    char ipv6Choice;
};

typedef int int32;

int readNetConfig(char * device, iface_t * iface,
                  char * dhcpclass, int methodNum);
int configureTCPIP(char * device, iface_t * iface, struct netconfopts * opts,
                   int methodNum);
int manualNetConfig(char * device, iface_t * iface,
                    struct intfconfig_s * ipcomps, struct netconfopts * opts);
void debugNetworkInfo(iface_t * iface);
int writeDisabledNetInfo(void);
int writeEnabledNetInfo(iface_t * iface);
int chooseNetworkInterface(struct loaderData_s * loaderData);
void setupNetworkDeviceConfig(iface_t * iface,
                              struct loaderData_s * loaderData);
int setupWireless(iface_t * iface);
void setKickstartNetwork(struct loaderData_s * loaderData, int argc, 
                         char ** argv);
int kickstartNetworkUp(struct loaderData_s * loaderData,
                       iface_t * iface);
void splitHostname (char *str, char **host, char **port);
int get_connection(iface_t * iface);

#endif
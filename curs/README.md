Tanenbaum, Wetherall Computer Networks 5e
=========================================


Materiale online de curs:
- [carte pdf](http://www.uoitc.edu.iq/images/documents/informatics-institute/exam_materials/Computer%20Networks%20-%20A%20Tanenbaum%20-%205th%20edition.pdf)
- [sursa video lectures](https://media.pearsoncmg.com/ph/streaming/esm/tanenbaum5e_videonotes/tanenbaum_videoNotes.html)
- [slide-urile de la curs](http://nlp.unibuc.ro/people/liviu.html#Courses)
- [Cursul lui Avinash Kak pe securitate](https://engineering.purdue.edu/kak/compsec/NewLectures/)
- [Computer Networks: A Systems Approach](https://book.systemsapproach.org/foundation.html)

## Cuprins
- [I. Introduction, Protocols and Layering](#intro)
- [II. Web and Content Distribution](#web)
- [III. Transport Layer, Reliable Transport](#trans)
- [IV. Congestion Control](#congestion)
- [V. Packet Forwarding and Internetworking](#forwarding)
- [VI. Routing](#routing)
- [VII. Link Layer, Part A pdf](#datalink_a)
- [VIII. Link Layer, Part B](#datalink_b)
- [IX. Physical Layer (optional)](#nivel_fizic)
- [X. Quality of Service](#qos)
- [XI. Network Security](#security)


<a name="intro"></a> 
Introduction, Protocols and Layering [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=25)
------------------------------------

[1-1 Goals and Motivation](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-1_Goals_and_Motivation__/ph/streaming/esm/tanenbaum5e_videonotes/1_1_goals_motivation_cn5e.m4v "1-1 Goals and Motivation")  
[1-2 Uses of Networks](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-2_Uses_of_Networks__/ph/streaming/esm/tanenbaum5e_videonotes/1_2_network_uses_cn5e.m4v "1-2 Uses of Networks")  
[1-3 Network Components](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-3_Network_Components__/ph/streaming/esm/tanenbaum5e_videonotes/1_3_network_components_cn5e.m4v "1-3 Network Components")  
[1-4 Sockets](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-4_Sockets__/ph/streaming/esm/tanenbaum5e_videonotes/1_4_sockets_cn5e.m4v "1-4 Sockets")  
[1-5 Traceroute](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-5_Traceroute__/ph/streaming/esm/tanenbaum5e_videonotes/1_5_traceroute_cn5e.m4v "1-5 Traceroute")  
[1-6 Protocols and Layers](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-6_Protocols_and_Layers__/ph/streaming/esm/tanenbaum5e_videonotes/1_6_protocol_layers_cn5e.m4v "1-6 Protocols and Layers")  
[1-7 Reference Models](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-7_Reference_Models__/ph/streaming/esm/tanenbaum5e_videonotes/1_7_reference_layers_cn5e.m4v "1-7 Reference Models")  
[1-8 History of the Internet](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-8_History_of_the_Internet__/ph/streaming/esm/tanenbaum5e_videonotes/1_8_internet_history_cn5e.m4v "1-8 History of the Internet")  
[1-9 Lecture Outline](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.1-9_Lecture_Outline__/ph/streaming/esm/tanenbaum5e_videonotes/1_9_lecture_outline_cn5e.m4v "1-9 Lecture Outline")



<a name="web"></a>
Web and Content Distribution [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=670)
----------------------------

[8-1 Application Layer Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-1_Application_Layer_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/8_1_application_overview_cn5e.m4v "8-1 Application Layer Overview")  
[8-2 Domain Name System DNS, Part 1](https://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-2_Domain_Name_System_(DNS),_Part_1__/ph/streaming/esm/tanenbaum5e_videonotes/8_2_dns_cn5e.m4v)  
[8-3 Domain Name System DNS, Part 2](https://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-3_Domain_Name_System_(DNS),_Part%202__/ph/streaming/esm/tanenbaum5e_videonotes/8_3_dns_cn5e.m4v)  
[8-4 Introduction to HTTP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-4_Introduction_to_HTTP__/ph/streaming/esm/tanenbaum5e_videonotes/8_4_http_cn5e.m4v "8-4 Introduction to HTTP")  
[8-5 HTTP Performance](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-5_HTTP_Performance__/ph/streaming/esm/tanenbaum5e_videonotes/8_5_http_performance_cn5e.m4v "8-5 HTTP Performance")  
[8-6 HTTP Caching and Proxies](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-6_HTTP_Caching_and_Proxies__/ph/streaming/esm/tanenbaum5e_videonotes/8_6_http_caching_cn5e.m4v "8-6 HTTP Caching and Proxies")  
[8-7 Content Delivery Networks (CDNs)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-7_Content_Delivery_Networks_(CDNs)__/ph/streaming/esm/tanenbaum5e_videonotes/8_7_cdns_cn5e.m4v "8-7 Content Delivery Networks (CDNs)")  
[8-8 Future of HTTP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-8_Future_of_HTTP__/ph/streaming/esm/tanenbaum5e_videonotes/8_8_http_future_cn5e.m4v "8-8 Future of HTTP")  
[8-9 Peer-to-Peer Content Delivery (BitTorrent)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.8-9_Peer-to-Peer_Content_Delivery_(BitTorrent)__/ph/streaming/esm/tanenbaum5e_videonotes/8_9_p2p_cn5e.m4v "8-9 Peer-to-Peer Content Delivery (BitTorrent)")



<a name="trans"></a> 
Transport Layer, Reliable Transport [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=519)
-----------------------------------

[6-1 Transport Layer Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-1_Transport_Layer_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/6_1_transport_overview_cn5e.m4v "6-1 Transport Layer Overview")  
[6-2 User Datagram Protocol UDP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-2_User_Datagram_Protocol%20(UDP)__/ph/streaming/esm/tanenbaum5e_videonotes/6_2_udp_cn5e.m4v)  
[6-3 Connection Establishment](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-3_Connection_Establishment__/ph/streaming/esm/tanenbaum5e_videonotes/6_3_connection_establish_cn5e.m4v "6-3 Connection Establishment")  
[6-4 Connection Release](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-4_Connection_Release__/ph/streaming/esm/tanenbaum5e_videonotes/6_4_connection_release_cn5e.m4v "6-4 Connection Release")  
[6-5 Sliding Window](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-5_Sliding_Window__/ph/streaming/esm/tanenbaum5e_videonotes/6_5_sliding_window_cn5e.m4v "6-5 Sliding Window")  
[6-6 Flow Control](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-6_Flow_Control__/ph/streaming/esm/tanenbaum5e_videonotes/6_6_flow_control_cn5e.m4v "6-6 Flow Control")  
[6-7 Retransmission Timeouts](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-7_Retransmission_Timeouts__/ph/streaming/esm/tanenbaum5e_videonotes/6_7_timeouts_cn5e.m4v "6-7 Retransmission Timeouts")  
[6-8 Transmission Control Protocol (TCP)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.6-8_Transmission_Control_Protocol_(TCP)__/ph/streaming/esm/tanenbaum5e_videonotes/6_8_tcp_cn5e.m4v "6-8 Transmission Control Protocol (TCP)")

<a name="congestion"></a> 
Congestion Control [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=554)
------------------

[7-1 Congestion Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-1_Congestion_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/7_1_congestion_overview_cn5e.m4v "7-1 Congestion Overview")  
[7-2 Fairness of Allocations](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-2_Fairness_of_Allocations__/ph/streaming/esm/tanenbaum5e_videonotes/7_2_fairness_cn5e.m4v "7-2 Fairness of Allocations")  
[7-3 Additive Increase Multiplicative Decrease (AIMD)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-3_Additive_Increase_Multiplicative_Decrease_(AIMD)__/ph/streaming/esm/tanenbaum5e_videonotes/7_3_aimd_cn5e.m4v "7-3 Additive Increase Multiplicative Decrease (AIMD)")  
[7-4 History of TCP Congestion Control](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-4_History_of_TCP_Congestion_Control__/ph/streaming/esm/tanenbaum5e_videonotes/7_4_tcp_history_cn5e.m4v "7-4 History of TCP Congestion Control")  
[7-5 ACK Clocking](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-5_ACK_Clocking__/ph/streaming/esm/tanenbaum5e_videonotes/7_5_ack_clock_cn5e.m4v "7-5 ACK Clocking")  
[7-6 TCP Slow-Start](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-6_TCP_Slow-Start__/ph/streaming/esm/tanenbaum5e_videonotes/7_6_slow_start_cn5e.m4v "7-6 TCP Slow-Start")  
[7-7 TCP Fast Retransmit / Fast Recovery](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-7_TCP_Fast_Retransmit_-_Fast_Recovery__/ph/streaming/esm/tanenbaum5e_videonotes/7_7_fast_recovery_cn5e.m4v "7-7 TCP Fast Retransmit / Fast Recovery")  
[7-8 Explicit Congestion Notification (ECN)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.7-8_Explicit_Congestion_Notification_(ECN)__/ph/streaming/esm/tanenbaum5e_videonotes/7_8_ecn_cn5e.m4v "7-8 Explicit Congestion Notification (ECN)")



<a name="forwarding"></a> 
Packet Forwarding and Internetworking [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=379)
-------------------------------------

[4-1 Network Layer Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-1_Network_Layer_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/4_1_network_overview_cn5e.m4v "4-1 Network Layer Overview")  
[4-2 Network Services](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-2_Network_Services__/ph/streaming/esm/tanenbaum5e_videonotes/4_2_network_service_cn5e.m4v "4-2 Network Services")  
[4-3 Internetworking](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-3_Internetworking__/ph/streaming/esm/tanenbaum5e_videonotes/4_3_internetworking_cn5e.m4v "4-3 Internetworking")  
[4-4 IP Prefixes](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-4_IP_Prefixes__/ph/streaming/esm/tanenbaum5e_videonotes/4_4_ip_prefixes_cn5e.m4v "4-4 IP Prefixes")  
[4-5 IP Forwarding](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-5_IP_Forwarding__/ph/streaming/esm/tanenbaum5e_videonotes/4_5_ip_forwarding_cn5e.m4v "4-5 IP Forwarding")  
[4-6 Helping IP with ARP, DHCP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-6_Helping_IP_with_ARP,_DHCP__/ph/streaming/esm/tanenbaum5e_videonotes/4_6_ip_helpers_cn5e.m4v "4-6 Helping IP with ARP, DHCP")  
[4-7 Packet Fragmentation](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-7_Packet_Fragmentation__/ph/streaming/esm/tanenbaum5e_videonotes/4_7_fragmentation_cn5e.m4v "4-7 Packet Fragmentation")  
[4-8 IP Errors with ICMP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-8_IP_Errors_with_ICMP__/ph/streaming/esm/tanenbaum5e_videonotes/4_8_ip_errors_cn5e.m4v "4-8 IP Errors with ICMP")  
[4-9 IP Version 6](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-9_IP_Version_6__/ph/streaming/esm/tanenbaum5e_videonotes/4_9_ipv6_cn5e.m4v "4-9 IP Version 6")  
[4-10 Network Address Translation](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.4-10_Network_Address_Translation__/ph/streaming/esm/tanenbaum5e_videonotes/4_10_nat_cn5e.m4v "4-10 Network Address Translation")


<a name="routing"></a>
Routing [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=386)
-------

[5-1 Routing Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-1_Routing_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/5_1_routing_overview_cn5e.m4v "5-1 Routing Overview")  
[5-2 Shortest Path Routing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-2_Shortest_Path_Routing__/ph/streaming/esm/tanenbaum5e_videonotes/5_2_shortest_path_cn5e.m4v "5-2 Shortest Path Routing")  
[5-3 Computing Shortest Paths with Dijkstra](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-3_Computing_Shortest_Paths_with_Dijkstra__/ph/streaming/esm/tanenbaum5e_videonotes/5_3_dijkstra_cn5e.m4v "5-3 Computing Shortest Paths with Dijkstra")  
[5-4 Distance Vector Routing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-4_Distance_Vector_Routing__/ph/streaming/esm/tanenbaum5e_videonotes/5_4_distance_vector_cn5e.m4v "5-4 Distance Vector Routing")  
[5-5 Flooding](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-5_Flooding__/ph/streaming/esm/tanenbaum5e_videonotes/5_5_flooding_cn5e.m4v "5-5 Flooding")  
[5-6 Link State Routing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-6_Link_State_Routing__/ph/streaming/esm/tanenbaum5e_videonotes/5_6_link_state_cn5e.m4v "5-6 Link State Routing")  
[5-7 Equal-Cost Multi-path Routing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-7_Equal-Cost_Multi-path_Routing__/ph/streaming/esm/tanenbaum5e_videonotes/5_7_ecmp_cn5e.m4v "5-7 Equal-Cost Multi-path Routing")  
[5-8 Combining Hosts and Routers](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-8_Combining_Hosts_and_Routers__/ph/streaming/esm/tanenbaum5e_videonotes/5_8_hosts_router_cn5e.m4v "5-8 Combining Hosts and Routers")  
[5-9 Hierarchical Routing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-9_Hierarchical_Routing__/ph/streaming/esm/tanenbaum5e_videonotes/5_9_hierarchical_cn5e.m4v "5-9 Hierarchical Routing")  
[5-10 IP Prefix Aggregation and Subnets](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-10_IP_Prefix_Aggregation_and_Subnets__/ph/streaming/esm/tanenbaum5e_videonotes/5_10_aggregation_cn5e.m4v "5-10 IP Prefix Aggregation and Subnets")  
[5-11 Routing with Multiple Parties](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-11_Routing_with_Multiple_Parties__/ph/streaming/esm/tanenbaum5e_videonotes/5_11_policy_cn5e.m4v "5-11 Routing with Multiple Parties")  
[5-12 Border Gateway Protocol BGP](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.5-12_Border_Gateway_Protocol_(BGP)__/ph/streaming/esm/tanenbaum5e_videonotes/5_12_bgp_cn5e.m4v "5-12 Border Gateway Protocol (BGP)")




<a name="datalink_a"></a> 
Link Layer, Part A [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=218)
------------------

[3a-1 Overview of the Link Layer](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3a-1_Overview_of_the_Link_Layer__/ph/streaming/esm/tanenbaum5e_videonotes/3a_1_link_overview_cn5e.m4v "3a-1 Overview of the Link Layer")  
[3a-2 Framing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3a-2_Framing__/ph/streaming/esm/tanenbaum5e_videonotes/3a_2_framing_cn5e.m4v "3a-2 Framing")  
[3a-3 Error Coding Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3a-3_Error_Coding_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/3a_3_error_overview_cn5e.m4v "3a-3 Error Coding Overview")  
[3a-4 Error Detection](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3a-4_Error_Detection__/ph/streaming/esm/tanenbaum5e_videonotes/3a_4_error_detection_cn5e.m4v "3a-4 Error Detection")  
[3a-5 Error Correction](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3a-5_Error_Correction__/ph/streaming/esm/tanenbaum5e_videonotes/3a_5_error_correction_cn5e.m4v "3a-5 Error Correction")


<a name="datalink_b"></a> 
Link Layer, Part B [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=281)
------------------

[3b-1 Overview of the Link Layer](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-1_Overview_of_the_Link_Layer__/ph/streaming/esm/tanenbaum5e_videonotes/3b_1_link_overview_cn5e.m4v "3b-1 Overview of the Link Layer")  
[3b-2 Retransmissions](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-2_Retransmissions__/ph/streaming/esm/tanenbaum5e_videonotes/3b_2_arq_cn5e.m4v "3b-2 Retransmissions")  
[3b-3 Multiplexing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-3_Multiplexing__/ph/streaming/esm/tanenbaum5e_videonotes/3b_3_multiplexing_cn5e.m4v "3b-3 Multiplexing")  
[3b-4 Random Multiple Access](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-4_Random_Multiple_Access__/ph/streaming/esm/tanenbaum5e_videonotes/3b_4_random_access_cn5e.m4v "3b-4 Random Multiple Access")  
[3b-5 Wireless Multiple Access](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-5_Wireless_Multiple_Access__/ph/streaming/esm/tanenbaum5e_videonotes/3b_5_wireless_access_cn5e.m4v "3b-5 Wireless Multiple Access")  
[3b-6 Contention-Free Multiple Access](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-6_Contention-Free_Multiple_Access__/ph/streaming/esm/tanenbaum5e_videonotes/3b_6_contention_free_cn5e.m4v "3b-6 Contention-Free Multiple Access")  
[3b-7 LAN Switches](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-7_LAN_Switches__/ph/streaming/esm/tanenbaum5e_videonotes/3b_7_switches_cn5e.m4v "3b-7 LAN Switches")  
[3b-8 Switch Spanning Tree](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.3b-8_Switch_Spanning_Tree__/ph/streaming/esm/tanenbaum5e_videonotes/3b_8_spanning_tree_cn5e.m4v "3b-8 Switch Spanning Tree")


<a name="nivel_fizic"></a> 
Physical Layer (optional) [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=113)
--------------

[2-1 Overview of the Physical Layer](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.2-1_Overview_of_the_Physical_Layer__/ph/streaming/esm/tanenbaum5e_videonotes/2_1_physical_overview_cn5e.m4v "2-1 Overview of the Physical Layer")  
[2-2 Media](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.2-2_Media__/ph/streaming/esm/tanenbaum5e_videonotes/2_2_media_cn5e.m4v "2-2 Media")  
[2-3 Signals](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.2-3_Signals__/ph/streaming/esm/tanenbaum5e_videonotes/2_3_signals_cn5e.m4v "2-3 Signals")  
[2-4 Modulation](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.2-4_Modulation__/ph/streaming/esm/tanenbaum5e_videonotes/2_4_modulation_cn5e.m4v "2-4 Modulation")  
[2-5 Fundamental Limits](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.2-5_Fundamental_Limits__/ph/streaming/esm/tanenbaum5e_videonotes/2_5_limits_cn5e.m4v "2-5 Fundamental Limits")



<a name="qos"></a>
Quality of Service [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=721)
------------------

[9-1 QOS Overview](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-1_QOS_Overview__/ph/streaming/esm/tanenbaum5e_videonotes/9_1_qos_overview_cn5e.m4v "9-1 QOS Overview")  
[9-2 Real-time Transport](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-2_Real-time_Transport__/ph/streaming/esm/tanenbaum5e_videonotes/9_2_real_time_cn5e.m4v "9-2 Real-time Transport")  
[9-3 Streaming Media](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-3_Streaming_Media__/ph/streaming/esm/tanenbaum5e_videonotes/9_3_streaming_media_cn5e.m4v "9-3 Streaming Media")  
[9-4 Fair Queuing](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-4_Fair_Queuing__/ph/streaming/esm/tanenbaum5e_videonotes/9_4_fair_queuing_cn5e.m4v "9-4 Fair Queuing")  
[9-5 Traffic Shaping](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-5_Traffic_Shaping__/ph/streaming/esm/tanenbaum5e_videonotes/9_5_traffic_shaping_cn5e.m4v "9-5 Traffic Shaping")  
[9-6 Differentiated Services](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-6_Differentiated_Services__/ph/streaming/esm/tanenbaum5e_videonotes/9_6_diffserv_cn5e.m4v "9-6 Differentiated Services")  
[9-7 Rate and Delay Guarantees](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.9-7_Rate_and_Delay_Guarantees__/ph/streaming/esm/tanenbaum5e_videonotes/9_7_ratedelay_cn5e.m4v "9-7 Rate and Delay Guarantees")

<a name="security"></a>
Network Security [capitolul în pdf](http://index-of.es/Varios-2/Computer%20Networks%205th%20Edition.pdf#page=787)
----------------

[10-1 Network Security Introduction](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-1_Network_Security_Introduction__/ph/streaming/esm/tanenbaum5e_videonotes/10_1_network_security_cn5e.m4v "10-1 Network Security Introduction")  
[10-2 Message Confidentiality](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-2_Message_Confidentiality__/ph/streaming/esm/tanenbaum5e_videonotes/10_2_confidentiality_cn5e.m4v "10-2 Message Confidentiality")  
[10-3 Message Authentication](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-3_Message_Authentication__/ph/streaming/esm/tanenbaum5e_videonotes/10_3_authentication_cn5e.m4v "10-3 Message Authentication")  
[10-4 Wireless Security](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-4_Wireless_Security__/ph/streaming/esm/tanenbaum5e_videonotes/10_4_wireless_security_cn5e.m4v "10-4 Wireless Security")  
[10-5 Web Security](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-5_Web_Security__/ph/streaming/esm/tanenbaum5e_videonotes/10_5_web_security_cn5e.m4v "10-5 Web Security")  
[10-6 DNS Security](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-6_DNS_Security__/ph/streaming/esm/tanenbaum5e_videonotes/10_6_dns_security_cn5e.m4v "10-6 DNS Security")  
[10-7 Firewalls](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-7_Firewalls__/ph/streaming/esm/tanenbaum5e_videonotes/10_7_firewalls_cn5e.m4v "10-7 Firewalls")  
[10-8 Virtual Private Networks (VPNs)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-8_Virtual_Private_Networks_(VPNs)__/ph/streaming/esm/tanenbaum5e_videonotes/10_8_vpns_cn5e.m4v "10-8 Virtual Private Networks (VPNs)")  
[10-9 Distributed Denial of Service (DDOS)](http://mediaplayer.pearsoncmg.com/_ph_cc_ecs_set.title.10-9_Distributed_Denial_of_Service_(DDOS)__/ph/streaming/esm/tanenbaum5e_videonotes/10_9_ddos_cn5e.m4v "10-9 Distributed Denial of Service (DDOS)")

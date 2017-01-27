CREATE TABLE `ap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datestamp` datetime NOT NULL,
  `connected` tinyint(4) NOT NULL,
  `encryption` tinyint(4) NOT NULL,
  `wpa_flags` int(11) NOT NULL,
  `rsn_flags` int(11) NOT NULL,
  `ssid` varchar(40) CHARACTER SET latin1 NOT NULL,
  `freq` int(11) NOT NULL,
  `hwaddr` varchar(24) CHARACTER SET latin1 NOT NULL,
  `mode` int(11) NOT NULL,
  `maxbitrate` int(11) NOT NULL,
  `strength` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=80 DEFAULT CHARSET=utf8

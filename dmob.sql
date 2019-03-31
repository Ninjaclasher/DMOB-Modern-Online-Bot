/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dmob_contest`
--

DROP TABLE IF EXISTS `dmob_contest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_contest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `deleted` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_contest_problem`
--

DROP TABLE IF EXISTS `dmob_contest_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_contest_problem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_id` int(11) NOT NULL,
  `problem_position` tinyint(4) NOT NULL,
  `problem` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_game`
--

DROP TABLE IF EXISTS `dmob_game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_game` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel` char(18) NOT NULL,
  `contest` int(11) DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `window` int(10) unsigned DEFAULT NULL,
  `state` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_game_participation`
--

DROP TABLE IF EXISTS `dmob_game_participation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_game_participation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `game` int(11) NOT NULL,
  `user` char(18) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_dmob_game_participation_game` (`game`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_judge`
--

DROP TABLE IF EXISTS `dmob_judge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_judge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `key` text NOT NULL,
  `deleted` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_problem`
--

DROP TABLE IF EXISTS `dmob_problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_problem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `code` text NOT NULL,
  `author` char(18) NOT NULL,
  `time_limit` double unsigned NOT NULL,
  `memory_limit` int(10) unsigned NOT NULL,
  `point_value` smallint(5) unsigned NOT NULL,
  `is_public` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_submission`
--

DROP TABLE IF EXISTS `dmob_submission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_submission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `points` float NOT NULL,
  `total` float NOT NULL,
  `time` double NOT NULL,
  `memory` int(11) NOT NULL,
  `result` varchar(4) NOT NULL,
  `user` char(18) NOT NULL,
  `problem` text NOT NULL,
  `submission_time` datetime NOT NULL,
  `code` longtext NOT NULL,
  `deleted` tinyint(4) NOT NULL,
  `contest` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_dmob_submission_user` (`user`),
  KEY `idx_dmob_submission_contest` (`contest`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_submission_case`
--

DROP TABLE IF EXISTS `dmob_submission_case`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_submission_case` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `submission_id` int(11) NOT NULL,
  `points` float NOT NULL,
  `total` float NOT NULL,
  `time` double NOT NULL,
  `memory` int(11) NOT NULL,
  `result` varchar(4) NOT NULL,
  `case_num` int(11) NOT NULL,
  `batch` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `submission_id` (`submission_id`,`case_num`)
) ENGINE=InnoDB AUTO_INCREMENT=439 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_user`
--

DROP TABLE IF EXISTS `dmob_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_user` (
  `id` char(18) NOT NULL,
  `points` double NOT NULL DEFAULT '0',
  `language` text NOT NULL,
  `is_admin` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dmob_user_rating`
--

DROP TABLE IF EXISTS `dmob_user_rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmob_user_rating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` char(18) NOT NULL,
  `rating` smallint(6) NOT NULL,
  `volatility` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_dmob_user_rating_user` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

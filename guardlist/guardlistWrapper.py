# this import, even if not directly used, will take care of correctly setting the path and setting up the clr
# see __init__.py in package
import GuardlistPython

from Microsoft.Office.Guardlist.Client import (EnvironmentType,
                                               GuardlistInput,
                                               GuardlistMetricsReporter,
                                               GuardlistMetricsReporterParams,
                                               GuardlistNLXClient,
                                               GuardlistClientNLXFactory,
                                               IDataMatcher,
                                               IGuardlistNLXClient,
                                               LanguageEnum,
                                               LocalNLXDataMatcher,
                                               ListDirectory,
                                               RemoteNLXDataMatcher,
                                               RemoteNLXDataMatcherParams,
                                               RemoteDownloadClient,
                                               SilentLogger,
                                               TermCategoryEnum,
                                               TermType)
from Microsoft.Office.Guardlist.Client.PythonWrapper import LoggingUtils
from Microsoft.Extensions.Logging import ILogger
from System import Func, String, TimeSpan
from System.Collections.Generic import List

class GuardlistWrapper:
    """
    Example class that wraps Microsoft.Office.Guardlist.Client and leverages the provided Factory method

    Partners can create something similar and update accordingly, mainly setting their own appKey and partnerName as
    well as specifying the list, refresh time and how to react to the metadata returned by Guardlist
    """
    appKey = "<appKey>"                               # contact guardlistworkgroup to get you appKey
    partnerName = "TestFromPython"                    # partnerName is used for reporting purposes, please use something meaningfull
                                                      # partners in hosted environments (such as AugmentatioLoop, 3S or Polymer) should prefix the name with their host
                                                      # for example: AL-CoolFeature, 3S-SmartFeature or Polymer-TextPredictorModel

    @staticmethod
    def createClient(appKey, partnerName, logger):
        """
        Callback from Guardlist when it needs to create a new client if one was not found registered already

        Args:
            appKey: the appKey to use

            partnerName: name of partner (for metric reporting purposes)

            logger: ILogger instance

        Returns:
            IGuardlistNLXClient instance that will then be cached
        """
        # specify which list to use
        listToUse = ListDirectory.OfficeWithMetadataNLX

        # initialize the local data, that will be used in case remote data retrieval fails
        localDataMatcher = LocalNLXDataMatcher(appKey,      # appKey
                                               listToUse,   # data to use
                                               logger)      # ILogger
        localDataMatcher.InitializeAsync().Wait()

        # set up the remote data parameters
        remoteNLXDataMatcherParams = RemoteNLXDataMatcherParams(None,                       # baseUri
                                                                3,                          # numberOfAttempts
                                                                TimeSpan.FromSeconds(10),   # attemptWaitTime
                                                                TimeSpan.FromMinutes(20),   # refreshInterval
                                                                TimeSpan.FromSeconds(60),   # mutexWaitTime
                                                                EnvironmentType.Prod,       # environment
                                                                None)                       # resourceFolder

        # initialize remote data
        remoteNLXDataMatcher = RemoteNLXDataMatcher(appKey,                                 # appKey
                                                    listToUse,                              # data to use
                                                    logger,                                 # ILogger
                                                    localDataMatcher,                       # fallbackDataMatcher
                                                    RemoteDownloadClient(logger),           # IDownloadClient
                                                    remoteNLXDataMatcherParams)             # RemoteNLXDataMatcherParams

        remoteNLXDataMatcher.InitializeAsync().Wait()
        listDataMatchers = List[IDataMatcher]()

        # specify which data matchers to use; note that you can add multiple IDataMatchers to the collection, each targetting a different list
        listDataMatchers.Add(remoteNLXDataMatcher)

        # set up the parameter for the metrics reporter
        reporterParams = GuardlistMetricsReporterParams(EnvironmentType.Prod,      # environment type
                                                        None,                      # Uri to send diagnostics to (null for default)
                                                        TimeSpan.FromSeconds(10),  # diagnostics send interval
                                                        TimeSpan.FromSeconds(1))   # partial metrics computation interval

        # create metrics reporter; this is optional (null/None can be passed) but higly recommended to pass it. Only diagnostic data will be sent over the wire
        metricsReporter = GuardlistMetricsReporter(reporterParams, logger)

        # prepare the client
        client = GuardlistNLXClient(appKey, partnerName, listDataMatchers, metricsReporter)

        return client


    @staticmethod
    def match(phrase, language):
        """
        Perform actual match

        Args:
            phrase: phrase to verify
            language: language of the phrase (provided by partner)

        Returns:
            MatchDefinition returned by Guardlist
        """
        # you can define your own logger, here is shown how we can use the default console logger
        # if you are not interested in logging, you can pass Microsoft.Office.Guardlist.Client.SilentLogger
        # logger = LoggingUtils.CreateConsoleLogger()
        logger = SilentLogger()

        # you can use the provided factory (which does internal caching in static variables on C# side) or you can cache the GuardlistNLXClient instance yourself
        # we are showing the factory approach here, but both are acceptable

        # get or register the client
        factory = GuardlistClientNLXFactory(logger)
        guardlistClient = factory.GetOrRegisterClient(GuardlistWrapper.appKey,
                                                      GuardlistWrapper.partnerName,
                                                      Func[String, String, ILogger, IGuardlistNLXClient](GuardlistWrapper.createClient))

        # perform the actual match
        guardlistInput = GuardlistInput(phrase)
        matchDefinition = guardlistClient.Match(guardlistInput)

        return matchDefinition

    @staticmethod
    def is_phrase_problematic(phrase, language):
        """
        Match and apply scenario-specific logic, determining whether a given phrase/language is problrmatic; this is partner/scenario specific and not mean to be used as-is but rather as a guidance.
        Partners can put their own logic in a similar method. Please contact guardlistworkgroup if you need any guidance

        Args:
            phrase: phrase to verify
            language: language of the phrase (provided by partner); Guardlist won't currently use this, but partners can use it to decide which entries to react to.
                      For example, if you know the input language is English and a Finnish entry is returned, you may decided to ignore the entry.
                      Generally, we recommend always reacting to English entries, even for non-English input languages

        Returns: whether the provided input are classified as problematic. Note that while this example is a binary trye/false, partners can decide to implement more
                 granular feedback, depending on their particular scenario
        """
        matchDefinition = GuardlistWrapper.match(phrase, language)

        for match in matchDefinition.Matches:
            # print(match.Term.Value)
            for metadata in match.Term.Metadata:
                # print('\t', metadata.Type, metadata.Category, metadata.Language)

                # if you desire, you can verify if the returned language matches one you are interested in
                # note that Guardlist can retun En, but also EnUS or EnCA, hence the use of "in" operator
                languageString = metadata.Language.ToString().lower()
                if not language.lower() in languageString:
                    # print('For a different language: ', language.lower(), 'Vs', languageString)
                    continue

                # you can also access the LanguageEnum directly
                if metadata.Language != LanguageEnum.En:
                    continue

                # we can check if it's HighRisk (should always be blocked)
                if metadata.Type == TermType.HighRisk:
                    return True

                # in case of ContextDependent entries, you can make use of the Category and TermCategoryEnum to take the action
                # that makes sense in our particular scenario
                if metadata.Type == TermType.ContextDependent:
                    if metadata.Category == TermCategoryEnum.Abuse:
                        return True

        return False

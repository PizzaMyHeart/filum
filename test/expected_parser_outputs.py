# flake8: noqa

expected_output_se = {
    'parent_data': {
        'title': 'Tableau not Recognizing Snowflake ODBC Drivers on Mac',
        'body': "\n\n\n\n\n\n\n\n\n\n**The [bounty](https://stackoverflow.com/help/bounty) expires in 5 hours**. Answers to this question are eligible for a +150 reputation bounty.\n [ZsideZ](/users/7072164/zsidez) is looking for an **answer from a reputable source**:\n \n> \n> I have the same problem :( HELP\n> \n\n\n\n\n\n\n\n\ni have a macbook with tableau desktop. i am trying to connect to snowflake, but tableau is not recognizing the snowflake odbc driver. i followed the steps in snowflake documentation to install the drivers. the files are in the correct folders, but i don't think the driver is actually installing.\n\n\ni have monterey OS. my colleague who has catalina has had no problem connecting to snowflake, while another colleague who also has monterey, is having the same issue i am. it seems like it may be because the file /usr/bin/python in catalina is renamed usr/bin/python3 in monterey.\n\n\nis there any way i can get my machine connected to snowflake using tableau on monterey?\n\n\n", 'author': 'Ryan McDermott', 'id': '72349922', 'score': '0', 'permalink': 'https://stackoverflow.com/questions/72349922/tableau-not-recognizing-snowflake-odbc-drivers-on-mac',
        'source': 'se',
        'posted_timestamp': 1653311062.0,
        'saved_timestamp': 1654174948.567066},
    'comment_data': {
        '127815671': {
            'author': 'Sergiu',
            'text': 'A few questions: what version of ODBC have you installed? Are you using a MAC with M1 chip or Intel? Are you able to use isql to test the connection to Snowflake?',
            'ancestor_id': '72349922',
            'depth': 2,
            'score': '0'
        },
        '127972756': {
            'author': 'Srinath Menon',
            'text': "If it is not specific that you need to have ODBC driver to connect to Tableau, then using the Tableau's native driver to connect to Snowflake would be the easiest approach to take.",
            'ancestor_id': '72349922',
            'depth': 2,
            'score': '0'
        },
        '72381195': {
            'author': 'Dave Welden',
            'text': '\nFirst, have you tried using [Snowflake Connectivity Diagnostic Tools](https://docs.snowflake.com/en/user-guide/snowcd.html) to verify your network connection is good and you can connect to Snowflake? If yes, then please try to connect to Snowflake using [SnowSQL](https://docs.snowflake.com/en/user-guide/snowsql.html) to verify your ODBC install. If both of these are successful, and you have followed [how to connect Tableau to a Snowflake data warehouse and set up the data source](https://help.tableau.com/current/pro/desktop/en-us/examples_snowflake.htm), then I would suggest you [start a support case with Tableau](https://www.tableau.com/support/case).\n\n\n',
            'ancestor_id': '72349922',
            'depth': 1,
            'score': '0',
            'timestamp': 1653492024.0,
            'permalink': 'https://stackoverflow.com/a/72381195'
        },
        '72411712': {
            'author': 'tagyoureit',
            'text': "\nNavigate to `~/Library/ODBC/odbcinst.ini`. You might be missing the DSN entry. If so, you can manually add the following:\n\n\n\n```\n[Snowflake]\nDriver = /opt/snowflake/snowflakeodbc/lib/universal/libSnowflake.dylib\n\n```\n\nSnowflake recommends <http://www.odbcmanager.net/>, but even with that I've previously had trouble adding the DSN and needed to manually add it.\n\n\n",
            'ancestor_id': '72349922',
            'depth': 1,
            'score': '0',
            'timestamp': 1653687999.0,
            'permalink': 'https://stackoverflow.com/a/72411712'
            }
        }
    }
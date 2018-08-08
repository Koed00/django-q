# Change Log

## [v0.9.4](https://github.com/koed00/django-q/tree/v0.9.4) (2018-03-13)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.9.3...v0.9.4)

## [v0.9.3](https://github.com/koed00/django-q/tree/v0.9.3) (2018-03-13)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.9.2...v0.9.3)

**Closed issues:**

- \[Wishlist\] Please provide a changelog in a text format in your repo. [\#293](https://github.com/Koed00/django-q/issues/293)
- django-q collides with existing app of name `tasks` [\#199](https://github.com/Koed00/django-q/issues/199)

**Merged pull requests:**

- Add option for acknowledging failed tasks \(globally and per-task\) [\#298](https://github.com/Koed00/django-q/pull/298) ([Balletie](https://github.com/Balletie))
- Changing the path location where Django-Q is inserted. [\#297](https://github.com/Koed00/django-q/pull/297) ([Eagllus](https://github.com/Eagllus))

## [v0.9.2](https://github.com/koed00/django-q/tree/v0.9.2) (2018-02-13)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.9.1...v0.9.2)

**Closed issues:**

- \[Debian\] The new release contains a python3-only line. [\#291](https://github.com/Koed00/django-q/issues/291)
- Support Python 3.x Only Since 0.9.0? [\#286](https://github.com/Koed00/django-q/issues/286)
- Error when using error reporters - AttributeError: 'generator' object has no attribute 'load' [\#276](https://github.com/Koed00/django-q/issues/276)
- Question: how to show the running task on the django-admin with redis as broker [\#270](https://github.com/Koed00/django-q/issues/270)
- Overflow on repeats fields [\#255](https://github.com/Koed00/django-q/issues/255)
- apps.py: Attempted relative import with no known parent package [\#249](https://github.com/Koed00/django-q/issues/249)
- Django and Django Q on different server with Redis as broker [\#237](https://github.com/Koed00/django-q/issues/237)
- The `django\_q/tests` directory isn't in the tarball [\#226](https://github.com/Koed00/django-q/issues/226)
- django scrapy project can't connect to redis [\#217](https://github.com/Koed00/django-q/issues/217)
- django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet. [\#216](https://github.com/Koed00/django-q/issues/216)
- Add Sentry support [\#210](https://github.com/Koed00/django-q/issues/210)
- Tasks in the queue are not being processed [\#203](https://github.com/Koed00/django-q/issues/203)
- Result is - [\#176](https://github.com/Koed00/django-q/issues/176)
- ERROR invalid syntax \(\<unknown\>, line 1\) - while passing objects as arguments [\#170](https://github.com/Koed00/django-q/issues/170)
- "InterfaceError: connection already closed" being raised when a test is run [\#167](https://github.com/Koed00/django-q/issues/167)
- AppRegistryNotReady Exception on Django 1.10 Dev [\#164](https://github.com/Koed00/django-q/issues/164)
- Retry possibility? [\#118](https://github.com/Koed00/django-q/issues/118)

**Merged pull requests:**

- Fix python3 only code [\#292](https://github.com/Koed00/django-q/pull/292) ([Eagllus](https://github.com/Eagllus))

## [v0.9.1](https://github.com/koed00/django-q/tree/v0.9.1) (2018-02-02)
[Full Changelog](https://github.com/koed00/django-q/compare/0.9.0...v0.9.1)

**Closed issues:**

- Django 2.0 admin last run urls  [\#289](https://github.com/Koed00/django-q/issues/289)
- The model Schedule is already registered [\#285](https://github.com/Koed00/django-q/issues/285)

**Merged pull requests:**

- Fix urls being escaped by admin [\#290](https://github.com/Koed00/django-q/pull/290) ([Eagllus](https://github.com/Eagllus))
- fixing entry\_points annotation to expose class rather than module [\#287](https://github.com/Koed00/django-q/pull/287) ([danielwelch](https://github.com/danielwelch))
- Allow SQS to use environment variables [\#283](https://github.com/Koed00/django-q/pull/283) ([svdgraaf](https://github.com/svdgraaf))

## [0.9.0](https://github.com/koed00/django-q/tree/0.9.0) (2018-01-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.9.0...0.9.0)

## [v0.9.0](https://github.com/koed00/django-q/tree/v0.9.0) (2018-01-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.8.1...v0.9.0)

**Closed issues:**

- Django-q calls task twice or more [\#183](https://github.com/Koed00/django-q/issues/183)

**Merged pull requests:**

- Django 2 compatiblity [\#279](https://github.com/Koed00/django-q/pull/279) ([Eagllus](https://github.com/Eagllus))
- fix usage of iter\_entry\_points [\#278](https://github.com/Koed00/django-q/pull/278) ([danielwelch](https://github.com/danielwelch))
- Updates Travis to test for Django 2 and the LTS versions [\#274](https://github.com/Koed00/django-q/pull/274) ([Koed00](https://github.com/Koed00))
- Django 2.0 compatibility [\#269](https://github.com/Koed00/django-q/pull/269) ([achidlow](https://github.com/achidlow))

## [v0.8.1](https://github.com/koed00/django-q/tree/v0.8.1) (2017-10-12)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.8.0...v0.8.1)

**Closed issues:**

- Django Q tasks are not executed with ./manage.py test [\#266](https://github.com/Koed00/django-q/issues/266)
- Unable to delete scheduled task item that was created in the admin. [\#258](https://github.com/Koed00/django-q/issues/258)
- \<mistake\> [\#257](https://github.com/Koed00/django-q/issues/257)
- Failed tasks and Chain [\#254](https://github.com/Koed00/django-q/issues/254)
- async and chains returns different task id ! [\#244](https://github.com/Koed00/django-q/issues/244)
- Python3. Async hook doesn't seem to work [\#240](https://github.com/Koed00/django-q/issues/240)
- Workers stall and do nothing [\#239](https://github.com/Koed00/django-q/issues/239)
- How is logging handled [\#209](https://github.com/Koed00/django-q/issues/209)
- ask close\_old\_connections use! [\#198](https://github.com/Koed00/django-q/issues/198)

**Merged pull requests:**

- Updates botocore, certifi, chardet, docutils, idna and psutil [\#267](https://github.com/Koed00/django-q/pull/267) ([Koed00](https://github.com/Koed00))
- Replaces some relative imports [\#264](https://github.com/Koed00/django-q/pull/264) ([Koed00](https://github.com/Koed00))
- Updates packages and Django version [\#263](https://github.com/Koed00/django-q/pull/263) ([Koed00](https://github.com/Koed00))
- Use 32 bits integer for repeat field to avoid overflow with frequent scheduled tasks [\#262](https://github.com/Koed00/django-q/pull/262) ([gchardon-hiventy](https://github.com/gchardon-hiventy))
- Error reporter [\#261](https://github.com/Koed00/django-q/pull/261) ([danielwelch](https://github.com/danielwelch))
- Remove dependency `future` [\#247](https://github.com/Koed00/django-q/pull/247) ([benjaoming](https://github.com/benjaoming))

## [v0.8.0](https://github.com/koed00/django-q/tree/v0.8.0) (2017-04-05)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.18...v0.8.0)

**Closed issues:**

- How do you actually initiate periodic scheduled tasks in production [\#221](https://github.com/Koed00/django-q/issues/221)
- Enhancement: add signals [\#219](https://github.com/Koed00/django-q/issues/219)
- very slow performance with global sync: True setting vs. async\(sync=True\) [\#214](https://github.com/Koed00/django-q/issues/214)
- daemonic processes are not allowed to have children [\#211](https://github.com/Koed00/django-q/issues/211)
- send\_mail problem [\#202](https://github.com/Koed00/django-q/issues/202)
- Starting qcluster crashes python in OSX Sierra [\#201](https://github.com/Koed00/django-q/issues/201)
- How can I run django-q qcluster with supervisor process manager [\#196](https://github.com/Koed00/django-q/issues/196)
- Can't get attribute 'simple\_class\_factory' on module 'django.db.models.base' [\#191](https://github.com/Koed00/django-q/issues/191)
- \[Q\] ERROR reincarnated pusher Process-1:4439 after sudden death [\#188](https://github.com/Koed00/django-q/issues/188)
- Can not pass async\(\) non-core functions [\#178](https://github.com/Koed00/django-q/issues/178)

**Merged pull requests:**

- Update to Django 1.11 & Python 3.6 [\#230](https://github.com/Koed00/django-q/pull/230) ([Koed00](https://github.com/Koed00))
- Add django 1.11 support [\#228](https://github.com/Koed00/django-q/pull/228) ([bulv1ne](https://github.com/bulv1ne))
- Update tasks.rst [\#222](https://github.com/Koed00/django-q/pull/222) ([wirasto](https://github.com/wirasto))
- Add signals [\#220](https://github.com/Koed00/django-q/pull/220) ([abompard](https://github.com/abompard))
- fix a race condition in orm broker [\#213](https://github.com/Koed00/django-q/pull/213) ([yannpom](https://github.com/yannpom))
- Option to undaemonize workers and allows them to spawn child processes [\#212](https://github.com/Koed00/django-q/pull/212) ([yannpom](https://github.com/yannpom))
- Replace global Conf mangling with monkeypatch [\#208](https://github.com/Koed00/django-q/pull/208) ([Urth](https://github.com/Urth))
- Explaining how to handle tasks async with qcluster [\#204](https://github.com/Koed00/django-q/pull/204) ([Eagllus](https://github.com/Eagllus))
- supervisor example in Cluster documentation fix \#196 [\#197](https://github.com/Koed00/django-q/pull/197) ([GabLeRoux](https://github.com/GabLeRoux))
- Update brokers.rst [\#187](https://github.com/Koed00/django-q/pull/187) ([pyprism](https://github.com/pyprism))
- Package update 21 7 [\#184](https://github.com/Koed00/django-q/pull/184) ([Koed00](https://github.com/Koed00))
- Guard loop sleep made configurable [\#182](https://github.com/Koed00/django-q/pull/182) ([bob-r](https://github.com/bob-r))
- Add option to qinfo to print task IDs [\#173](https://github.com/Koed00/django-q/pull/173) ([Aninstance](https://github.com/Aninstance))
- Log id returned by broker [\#148](https://github.com/Koed00/django-q/pull/148) ([k4ml](https://github.com/k4ml))

## [v0.7.18](https://github.com/koed00/django-q/tree/v0.7.18) (2016-06-07)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.17...v0.7.18)

**Closed issues:**

- ValueError\('need more than 1 value to unpack',\) [\#171](https://github.com/Koed00/django-q/issues/171)
- Successful tasks are not being saved to the database when 'save\_limit' config setting is 0 [\#157](https://github.com/Koed00/django-q/issues/157)

**Merged pull requests:**

- Updates dependencies [\#175](https://github.com/Koed00/django-q/pull/175) ([Koed00](https://github.com/Koed00))
- Updates Django and some packages [\#169](https://github.com/Koed00/django-q/pull/169) ([Koed00](https://github.com/Koed00))

## [v0.7.17](https://github.com/koed00/django-q/tree/v0.7.17) (2016-04-24)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.16...v0.7.17)

**Closed issues:**

- Typo in parameter passed to broker in get\_broker [\#158](https://github.com/Koed00/django-q/issues/158)
- Circus stop only stops first process [\#155](https://github.com/Koed00/django-q/issues/155)
- Allow task custom name [\#146](https://github.com/Koed00/django-q/issues/146)
- Worker recycle causes: "ERROR connection already closed" [\#144](https://github.com/Koed00/django-q/issues/144)

**Merged pull requests:**

- Updates packages for testing [\#166](https://github.com/Koed00/django-q/pull/166) ([Koed00](https://github.com/Koed00))
- allow scheduler to schedule all pending tasks [\#165](https://github.com/Koed00/django-q/pull/165) ([thatmattbone](https://github.com/thatmattbone))
- Updates docs and tests for new Django versions [\#163](https://github.com/Koed00/django-q/pull/163) ([Koed00](https://github.com/Koed00))
- Fixes typo in custom broker handler [\#159](https://github.com/Koed00/django-q/pull/159) ([Koed00](https://github.com/Koed00))

## [v0.7.16](https://github.com/koed00/django-q/tree/v0.7.16) (2016-03-07)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.15...v0.7.16)

**Fixed bugs:**

- "connection already closed" while testing [\#127](https://github.com/Koed00/django-q/issues/127)
- Async argument 'timeout' fails if broker timeout is set to None [\#125](https://github.com/Koed00/django-q/issues/125)

**Closed issues:**

- Scheduled task name behaviour inconsistent [\#150](https://github.com/Koed00/django-q/issues/150)
- SystemError: Parent module '' not loaded, cannot perform relative import [\#142](https://github.com/Koed00/django-q/issues/142)
- OrmQ broker MySQL connection errors on ORM.delete\(task\_id\) [\#124](https://github.com/Koed00/django-q/issues/124)
- Task stays in queue when executing a requests.post [\#97](https://github.com/Koed00/django-q/issues/97)

**Merged pull requests:**

- Updates Django to 1.9.4 and 1.8.11 [\#153](https://github.com/Koed00/django-q/pull/153) ([Koed00](https://github.com/Koed00))
- Fixes for several issues [\#152](https://github.com/Koed00/django-q/pull/152) ([Koed00](https://github.com/Koed00))
- Updates to Django 1.8.9 and 1.9.2 [\#143](https://github.com/Koed00/django-q/pull/143) ([Koed00](https://github.com/Koed00))

## [v0.7.15](https://github.com/koed00/django-q/tree/v0.7.15) (2016-01-27)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.14...v0.7.15)

**Closed issues:**

- Make orm polling interval configurable [\#139](https://github.com/Koed00/django-q/issues/139)

**Merged pull requests:**

- Adds custom broker setting [\#141](https://github.com/Koed00/django-q/pull/141) ([Koed00](https://github.com/Koed00))
- Adds poll option for database brokers [\#140](https://github.com/Koed00/django-q/pull/140) ([Koed00](https://github.com/Koed00))

## [v0.7.14](https://github.com/koed00/django-q/tree/v0.7.14) (2016-01-24)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.13...v0.7.14)

**Closed issues:**

- app file structure [\#100](https://github.com/Koed00/django-q/issues/100)

**Merged pull requests:**

- Adds task result update [\#138](https://github.com/Koed00/django-q/pull/138) ([Koed00](https://github.com/Koed00))
- Save task now creates or updates [\#136](https://github.com/Koed00/django-q/pull/136) ([Koed00](https://github.com/Koed00))
- Fixes acknowledgement bug for failed tasks [\#135](https://github.com/Koed00/django-q/pull/135) ([Koed00](https://github.com/Koed00))
- Removes duplicate test [\#134](https://github.com/Koed00/django-q/pull/134) ([Koed00](https://github.com/Koed00))

## [v0.7.13](https://github.com/koed00/django-q/tree/v0.7.13) (2016-01-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.12...v0.7.13)

## [v0.7.12](https://github.com/koed00/django-q/tree/v0.7.12) (2016-01-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.11...v0.7.12)

**Closed issues:**

- Bug? Hourly schedule\_type runs in reverse [\#128](https://github.com/Koed00/django-q/issues/128)
- scheduling repeating tasks [\#121](https://github.com/Koed00/django-q/issues/121)
- documentation or design issue? [\#114](https://github.com/Koed00/django-q/issues/114)
- Catch\_up States [\#110](https://github.com/Koed00/django-q/issues/110)
- foo.bar.tasks.my\_task fails with "No module named bar.tasks" when running in AWS / Elastic Beanstalk [\#105](https://github.com/Koed00/django-q/issues/105)
- Q Cluster auto-launch? [\#102](https://github.com/Koed00/django-q/issues/102)

**Merged pull requests:**

- v0.7.12 [\#132](https://github.com/Koed00/django-q/pull/132) ([Koed00](https://github.com/Koed00))
- Adds Rollbar support for exceptions [\#131](https://github.com/Koed00/django-q/pull/131) ([Koed00](https://github.com/Koed00))
- Updates packages and Django for testing [\#130](https://github.com/Koed00/django-q/pull/130) ([Koed00](https://github.com/Koed00))
- Fix for unusable ORM Broker connections [\#126](https://github.com/Koed00/django-q/pull/126) ([kdmukai](https://github.com/kdmukai))
- Adds a check for duplicate schedule names. [\#123](https://github.com/Koed00/django-q/pull/123) ([Koed00](https://github.com/Koed00))
- fixed typo [\#117](https://github.com/Koed00/django-q/pull/117) ([Eagllus](https://github.com/Eagllus))
- Update example to use string for the schedule\_type [\#115](https://github.com/Koed00/django-q/pull/115) ([Eagllus](https://github.com/Eagllus))
- Updates Blessed [\#113](https://github.com/Koed00/django-q/pull/113) ([Koed00](https://github.com/Koed00))
- docs: rephrased the missing schedule description [\#112](https://github.com/Koed00/django-q/pull/112) ([Koed00](https://github.com/Koed00))
- Updates botocore for testing [\#111](https://github.com/Koed00/django-q/pull/111) ([Koed00](https://github.com/Koed00))
- Updates Django [\#109](https://github.com/Koed00/django-q/pull/109) ([Koed00](https://github.com/Koed00))
- Updates botocore for testing [\#108](https://github.com/Koed00/django-q/pull/108) ([Koed00](https://github.com/Koed00))

## [v0.7.11](https://github.com/koed00/django-q/tree/v0.7.11) (2015-10-28)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.10...v0.7.11)

**Closed issues:**

- fetch\(\) only works for the first task, returning None for subsequent tasks IDs [\#99](https://github.com/Koed00/django-q/issues/99)

**Merged pull requests:**

- docs:  added Async class [\#104](https://github.com/Koed00/django-q/pull/104) ([Koed00](https://github.com/Koed00))
- adds `Async` class [\#103](https://github.com/Koed00/django-q/pull/103) ([Koed00](https://github.com/Koed00))
- Adds timeout to group key cache object [\#98](https://github.com/Koed00/django-q/pull/98) ([Koed00](https://github.com/Koed00))

## [v0.7.10](https://github.com/koed00/django-q/tree/v0.7.10) (2015-10-19)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.9...v0.7.10)

**Merged pull requests:**

- Adds task chains [\#96](https://github.com/Koed00/django-q/pull/96) ([Koed00](https://github.com/Koed00))
- Updates botocore for testing [\#95](https://github.com/Koed00/django-q/pull/95) ([Koed00](https://github.com/Koed00))
- Updates Requests and Blessed requirements for testing [\#94](https://github.com/Koed00/django-q/pull/94) ([Koed00](https://github.com/Koed00))
- Updates Arrow and Blessed for testing [\#93](https://github.com/Koed00/django-q/pull/93) ([Koed00](https://github.com/Koed00))
- Updates botocore for testing [\#92](https://github.com/Koed00/django-q/pull/92) ([Koed00](https://github.com/Koed00))

## [v0.7.9](https://github.com/koed00/django-q/tree/v0.7.9) (2015-10-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.8...v0.7.9)

**Merged pull requests:**

- Updated botocore for testing [\#91](https://github.com/Koed00/django-q/pull/91) ([Koed00](https://github.com/Koed00))
- adds version info to qinfo [\#90](https://github.com/Koed00/django-q/pull/90) ([Koed00](https://github.com/Koed00))
- Adds version and broker info to qinfo [\#89](https://github.com/Koed00/django-q/pull/89) ([Koed00](https://github.com/Koed00))
- Updates botocore, requests and six for testing [\#88](https://github.com/Koed00/django-q/pull/88) ([Koed00](https://github.com/Koed00))
- adds `cached` option to `async\_iter` [\#87](https://github.com/Koed00/django-q/pull/87) ([Koed00](https://github.com/Koed00))
- moves hook signal in separate module [\#86](https://github.com/Koed00/django-q/pull/86) ([Koed00](https://github.com/Koed00))
- Updates psutil to 3.2.2 [\#85](https://github.com/Koed00/django-q/pull/85) ([Koed00](https://github.com/Koed00))

## [v0.7.8](https://github.com/koed00/django-q/tree/v0.7.8) (2015-10-04)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.7...v0.7.8)

**Merged pull requests:**

- Adds cached result backend [\#84](https://github.com/Koed00/django-q/pull/84) ([Koed00](https://github.com/Koed00))
- Update tests for Django 1.8.5 [\#83](https://github.com/Koed00/django-q/pull/83) ([Koed00](https://github.com/Koed00))
- updates botocore to 1.2.6 for testing [\#81](https://github.com/Koed00/django-q/pull/81) ([Koed00](https://github.com/Koed00))

## [v0.7.7](https://github.com/koed00/django-q/tree/v0.7.7) (2015-09-29)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.6...v0.7.7)

## [v0.7.6](https://github.com/koed00/django-q/tree/v0.7.6) (2015-09-29)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.5...v0.7.6)

**Closed issues:**

- Cluster dies when started with Postgres [\#79](https://github.com/Koed00/django-q/issues/79)

**Merged pull requests:**

- \#79  close django db connection before fork [\#80](https://github.com/Koed00/django-q/pull/80) ([Koed00](https://github.com/Koed00))

## [v0.7.5](https://github.com/koed00/django-q/tree/v0.7.5) (2015-09-28)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.4...v0.7.5)

**Closed issues:**

- Getting "MySQL server has gone away" on new tasks after idling [\#76](https://github.com/Koed00/django-q/issues/76)

**Merged pull requests:**

- docs: mention Django 1.9a1 support [\#78](https://github.com/Koed00/django-q/pull/78) ([Koed00](https://github.com/Koed00))
- Adds stale db connection check before every transaction [\#77](https://github.com/Koed00/django-q/pull/77) ([Koed00](https://github.com/Koed00))

## [v0.7.4](https://github.com/koed00/django-q/tree/v0.7.4) (2015-09-26)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.3...v0.7.4)

**Merged pull requests:**

- Adds MongoDB broker [\#75](https://github.com/Koed00/django-q/pull/75) ([Koed00](https://github.com/Koed00))
- Removes root imports [\#74](https://github.com/Koed00/django-q/pull/74) ([Koed00](https://github.com/Koed00))
- Removes pycharm stdin bug workaround [\#73](https://github.com/Koed00/django-q/pull/73) ([Koed00](https://github.com/Koed00))
- adds compatibility section to docs [\#72](https://github.com/Koed00/django-q/pull/72) ([Koed00](https://github.com/Koed00))
- Only show lock count when available and greater than zero [\#71](https://github.com/Koed00/django-q/pull/71) ([Koed00](https://github.com/Koed00))
- Python 3.5 compatibility [\#70](https://github.com/Koed00/django-q/pull/70) ([Koed00](https://github.com/Koed00))
- docs: Replaced redis pooling with broker pooling example. [\#69](https://github.com/Koed00/django-q/pull/69) ([Koed00](https://github.com/Koed00))

## [v0.7.3](https://github.com/koed00/django-q/tree/v0.7.3) (2015-09-18)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.2...v0.7.3)

**Merged pull requests:**

- Adds a wait option for results. [\#68](https://github.com/Koed00/django-q/pull/68) ([Koed00](https://github.com/Koed00))

## [v0.7.2](https://github.com/koed00/django-q/tree/v0.7.2) (2015-09-17)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.1...v0.7.2)

**Merged pull requests:**

- orm: Improves locking behavior [\#67](https://github.com/Koed00/django-q/pull/67) ([Koed00](https://github.com/Koed00))
- tests orm queue admin overrides [\#66](https://github.com/Koed00/django-q/pull/66) ([Koed00](https://github.com/Koed00))
- Adds remote orm admin view [\#65](https://github.com/Koed00/django-q/pull/65) ([Koed00](https://github.com/Koed00))

## [v0.7.1](https://github.com/koed00/django-q/tree/v0.7.1) (2015-09-16)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.7.0...v0.7.1)

**Merged pull requests:**

- Adds configuration output and other enhancements [\#64](https://github.com/Koed00/django-q/pull/64) ([Koed00](https://github.com/Koed00))

## [v0.7.0](https://github.com/koed00/django-q/tree/v0.7.0) (2015-09-14)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.6.4...v0.7.0)

**Merged pull requests:**

- Adds Django ORM broker [\#63](https://github.com/Koed00/django-q/pull/63) ([Koed00](https://github.com/Koed00))
- Updated wcwidth [\#62](https://github.com/Koed00/django-q/pull/62) ([Koed00](https://github.com/Koed00))
- Adds Fastack option to Disque broker [\#61](https://github.com/Koed00/django-q/pull/61) ([Koed00](https://github.com/Koed00))
- Updates test dependencies [\#60](https://github.com/Koed00/django-q/pull/60) ([Koed00](https://github.com/Koed00))

## [v0.6.4](https://github.com/koed00/django-q/tree/v0.6.4) (2015-09-10)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.6.3...v0.6.4)

**Closed issues:**

- `qcluster` command doesn't handle interrupts.  [\#56](https://github.com/Koed00/django-q/issues/56)

**Merged pull requests:**

- Adds Amazon SQS broker [\#58](https://github.com/Koed00/django-q/pull/58) ([Koed00](https://github.com/Koed00))
- \#56 cpu\_affinity not supported on some platforms [\#57](https://github.com/Koed00/django-q/pull/57) ([Koed00](https://github.com/Koed00))
- docs: `cache` option [\#55](https://github.com/Koed00/django-q/pull/55) ([Koed00](https://github.com/Koed00))

## [v0.6.3](https://github.com/koed00/django-q/tree/v0.6.3) (2015-09-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.6.2...v0.6.3)

**Merged pull requests:**

- Adds IronMQ broker [\#54](https://github.com/Koed00/django-q/pull/54) ([Koed00](https://github.com/Koed00))

## [v0.6.2](https://github.com/koed00/django-q/tree/v0.6.2) (2015-09-07)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.6.1...v0.6.2)

**Merged pull requests:**

- Fixes backward compatibility problems with django-picklefield [\#53](https://github.com/Koed00/django-q/pull/53) ([Koed00](https://github.com/Koed00))

## [v0.6.1](https://github.com/koed00/django-q/tree/v0.6.1) (2015-09-07)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.6.0...v0.6.1)

## [v0.6.0](https://github.com/koed00/django-q/tree/v0.6.0) (2015-09-06)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.5.3...v0.6.0)

**Merged pull requests:**

- Adds pluggable brokers [\#52](https://github.com/Koed00/django-q/pull/52) ([Koed00](https://github.com/Koed00))
- \#50 adds psutil as alternative os.getppid provider [\#51](https://github.com/Koed00/django-q/pull/51) ([Koed00](https://github.com/Koed00))

## [v0.5.3](https://github.com/koed00/django-q/tree/v0.5.3) (2015-08-19)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.5.2...v0.5.3)

**Merged pull requests:**

- v0.5.3 [\#49](https://github.com/Koed00/django-q/pull/49) ([Koed00](https://github.com/Koed00))
- adds `catch\_up` configuration option [\#48](https://github.com/Koed00/django-q/pull/48) ([Koed00](https://github.com/Koed00))
- consolidates redis ping [\#47](https://github.com/Koed00/django-q/pull/47) ([Koed00](https://github.com/Koed00))

## [v0.5.2](https://github.com/koed00/django-q/tree/v0.5.2) (2015-08-13)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.5.1...v0.5.2)

**Merged pull requests:**

- Adds global `sync` configuration option [\#46](https://github.com/Koed00/django-q/pull/46) ([Koed00](https://github.com/Koed00))

## [v0.5.1](https://github.com/koed00/django-q/tree/v0.5.1) (2015-08-12)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.5.0...v0.5.1)

**Merged pull requests:**

- Adds `qinfo` management command [\#45](https://github.com/Koed00/django-q/pull/45) ([Koed00](https://github.com/Koed00))

## [v0.5.0](https://github.com/koed00/django-q/tree/v0.5.0) (2015-08-06)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.6...v0.5.0)

**Closed issues:**

- Too many workers [\#43](https://github.com/Koed00/django-q/issues/43)

**Merged pull requests:**

- Adds a n-minutes option to the scheduler [\#44](https://github.com/Koed00/django-q/pull/44) ([Koed00](https://github.com/Koed00))

## [v0.4.6](https://github.com/koed00/django-q/tree/v0.4.6) (2015-08-04)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.5...v0.4.6)

**Closed issues:**

- sem\_getvalue not implemented on OSX [\#40](https://github.com/Koed00/django-q/issues/40)

**Merged pull requests:**

- Replaces qsize == 0 with empty\(\) [\#42](https://github.com/Koed00/django-q/pull/42) ([Koed00](https://github.com/Koed00))
- Workaround for osx implementation [\#41](https://github.com/Koed00/django-q/pull/41) ([Koed00](https://github.com/Koed00))

## [v0.4.5](https://github.com/koed00/django-q/tree/v0.4.5) (2015-08-01)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.4...v0.4.5)

**Closed issues:**

- Getting 'can't pickle lock objects' using async\(\) [\#38](https://github.com/Koed00/django-q/issues/38)

**Merged pull requests:**

- Sets pickle protocol to highest [\#39](https://github.com/Koed00/django-q/pull/39) ([Koed00](https://github.com/Koed00))
- fixes save\_limit +1 [\#37](https://github.com/Koed00/django-q/pull/37) ([Koed00](https://github.com/Koed00))
- Moves unpacking task from Worker to Pusher [\#36](https://github.com/Koed00/django-q/pull/36) ([Koed00](https://github.com/Koed00))

## [v0.4.4](https://github.com/koed00/django-q/tree/v0.4.4) (2015-07-27)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.3...v0.4.4)

**Merged pull requests:**

- closes old db connections on monitor and worker spawn [\#35](https://github.com/Koed00/django-q/pull/35) ([Koed00](https://github.com/Koed00))
- Updated to future 0.15.0 [\#34](https://github.com/Koed00/django-q/pull/34) ([Koed00](https://github.com/Koed00))
- Group filter and queue limit indicator [\#33](https://github.com/Koed00/django-q/pull/33) ([Koed00](https://github.com/Koed00))

## [v0.4.3](https://github.com/koed00/django-q/tree/v0.4.3) (2015-07-24)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.2...v0.4.3)

**Merged pull requests:**

- Adds queue limit and encryption salt [\#32](https://github.com/Koed00/django-q/pull/32) ([Koed00](https://github.com/Koed00))
- adds Haystack example [\#31](https://github.com/Koed00/django-q/pull/31) ([Koed00](https://github.com/Koed00))

## [v0.4.2](https://github.com/koed00/django-q/tree/v0.4.2) (2015-07-22)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.1...v0.4.2)

**Closed issues:**

- Timeout doesn't work [\#28](https://github.com/Koed00/django-q/issues/28)

**Merged pull requests:**

- Minor linting and fixes [\#30](https://github.com/Koed00/django-q/pull/30) ([Koed00](https://github.com/Koed00))
- timeout as float [\#29](https://github.com/Koed00/django-q/pull/29) ([Koed00](https://github.com/Koed00))

## [v0.4.1](https://github.com/koed00/django-q/tree/v0.4.1) (2015-07-21)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.4.0...v0.4.1)

**Merged pull requests:**

- Adds `save` override options for tasks [\#27](https://github.com/Koed00/django-q/pull/27) ([Koed00](https://github.com/Koed00))
- Expanding coverage [\#26](https://github.com/Koed00/django-q/pull/26) ([Koed00](https://github.com/Koed00))

## [v0.4.0](https://github.com/koed00/django-q/tree/v0.4.0) (2015-07-19)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.5...v0.4.0)

**Merged pull requests:**

- Added a group example [\#25](https://github.com/Koed00/django-q/pull/25) ([Koed00](https://github.com/Koed00))
- Adds failure filtering to group functions [\#24](https://github.com/Koed00/django-q/pull/24) ([Koed00](https://github.com/Koed00))
- Adds count\_group\(\) and delete\_group\(\) [\#23](https://github.com/Koed00/django-q/pull/23) ([Koed00](https://github.com/Koed00))
- decoding values\_list on a picklefield is faster [\#22](https://github.com/Koed00/django-q/pull/22) ([Koed00](https://github.com/Koed00))
- Adds task groups [\#21](https://github.com/Koed00/django-q/pull/21) ([Koed00](https://github.com/Koed00))

## [v0.3.5](https://github.com/koed00/django-q/tree/v0.3.5) (2015-07-17)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.6...v0.3.5)

## [v0.3.6](https://github.com/koed00/django-q/tree/v0.3.6) (2015-07-17)
[Full Changelog](https://github.com/koed00/django-q/compare/0.3.5...v0.3.6)

**Merged pull requests:**

- Tests now run with logging level debug [\#20](https://github.com/Koed00/django-q/pull/20) ([Koed00](https://github.com/Koed00))
- docs: small edits [\#19](https://github.com/Koed00/django-q/pull/19) ([Koed00](https://github.com/Koed00))
- Adds a `timeout` override per task [\#18](https://github.com/Koed00/django-q/pull/18) ([Koed00](https://github.com/Koed00))
- Adds management commands to the tests [\#17](https://github.com/Koed00/django-q/pull/17) ([Koed00](https://github.com/Koed00))
- Docs: Added a report example [\#16](https://github.com/Koed00/django-q/pull/16) ([Koed00](https://github.com/Koed00))

## [0.3.5](https://github.com/koed00/django-q/tree/0.3.5) (2015-07-15)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.4...0.3.5)

**Merged pull requests:**

- Adds cpu affinity to workers [\#15](https://github.com/Koed00/django-q/pull/15) ([Koed00](https://github.com/Koed00))
- Clean up redis key after test [\#14](https://github.com/Koed00/django-q/pull/14) ([Koed00](https://github.com/Koed00))
- Adding sphinx build to Travis [\#13](https://github.com/Koed00/django-q/pull/13) ([Koed00](https://github.com/Koed00))
- Adding examples to the docs [\#12](https://github.com/Koed00/django-q/pull/12) ([Koed00](https://github.com/Koed00))

## [v0.3.4](https://github.com/koed00/django-q/tree/v0.3.4) (2015-07-12)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.3...v0.3.4)

**Merged pull requests:**

- Testing with Arrow 0.6.0 now [\#11](https://github.com/Koed00/django-q/pull/11) ([Koed00](https://github.com/Koed00))
- Schedules of type ONCE will selfdestruct with negative repeats [\#10](https://github.com/Koed00/django-q/pull/10) ([Koed00](https://github.com/Koed00))

## [v0.3.3](https://github.com/koed00/django-q/tree/v0.3.3) (2015-07-10)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.2...v0.3.3)

**Closed issues:**

- Documentation for mocking in case of testing [\#7](https://github.com/Koed00/django-q/issues/7)

**Merged pull requests:**

- Fixes save pruning bug [\#9](https://github.com/Koed00/django-q/pull/9) ([Koed00](https://github.com/Koed00))

## [v0.3.2](https://github.com/koed00/django-q/tree/v0.3.2) (2015-07-09)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.1...v0.3.2)

**Closed issues:**

- No module named builtins [\#4](https://github.com/Koed00/django-q/issues/4)

**Merged pull requests:**

- Updated docs [\#6](https://github.com/Koed00/django-q/pull/6) ([Koed00](https://github.com/Koed00))
- Added 'future' to setup.py dependencies [\#5](https://github.com/Koed00/django-q/pull/5) ([nickpolet](https://github.com/nickpolet))

## [v0.3.1](https://github.com/koed00/django-q/tree/v0.3.1) (2015-07-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.3.0...v0.3.1)

## [v0.3.0](https://github.com/koed00/django-q/tree/v0.3.0) (2015-07-08)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.2.2...v0.3.0)

**Merged pull requests:**

- Switched to uuid4 instead of luid [\#3](https://github.com/Koed00/django-q/pull/3) ([Koed00](https://github.com/Koed00))

## [v0.2.2](https://github.com/koed00/django-q/tree/v0.2.2) (2015-07-07)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.2.1.1...v0.2.2)

**Merged pull requests:**

- Stabilizing stop procedures [\#2](https://github.com/Koed00/django-q/pull/2) ([Koed00](https://github.com/Koed00))

## [v0.2.1.1](https://github.com/koed00/django-q/tree/v0.2.1.1) (2015-07-06)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.2.1...v0.2.1.1)

## [v0.2.1](https://github.com/koed00/django-q/tree/v0.2.1) (2015-07-06)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.2.0...v0.2.1)

## [v0.2.0](https://github.com/koed00/django-q/tree/v0.2.0) (2015-07-04)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.4.1...v0.2.0)

## [v0.1.4.1](https://github.com/koed00/django-q/tree/v0.1.4.1) (2015-07-02)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.4...v0.1.4.1)

## [v0.1.4](https://github.com/koed00/django-q/tree/v0.1.4) (2015-07-01)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.3...v0.1.4)

## [v0.1.3](https://github.com/koed00/django-q/tree/v0.1.3) (2015-06-30)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.2...v0.1.3)

## [v0.1.2](https://github.com/koed00/django-q/tree/v0.1.2) (2015-06-30)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.1...v0.1.2)

## [v0.1.1](https://github.com/koed00/django-q/tree/v0.1.1) (2015-06-28)
[Full Changelog](https://github.com/koed00/django-q/compare/v0.1.0...v0.1.1)

## [v0.1.0](https://github.com/koed00/django-q/tree/v0.1.0) (2015-06-28)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
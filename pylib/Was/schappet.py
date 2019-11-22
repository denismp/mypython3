# [12/8/09 17:47:28:667 EST] New Application > Enterprise Applications
AdminApp.install('/tmp/DamnSchappettEA.ear', '[  -nopreCompileJSPs -distributeApp -nouseMetaDataFromBinary -nodeployejb -appname DamnSchappettEA -createMBeansForResources -noreloadEnabled -nodeployws -validateinstall warn -noprocessEmbeddedConfig -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 -noallowDispatchRemoteInclude -noallowServiceRemoteInclude -asyncRequestDispatchType DISABLED -nouseAutoLink -MapModulesToServers [[ SchappettWEB SchappettWEB.war,WEB-INF/web.xml WebSphere:cell=cell101,cluster=cl_cell101_a ]]]' )

# [12/8/09 17:47:40:834 EST] New Application > Enterprise Applications
AdminConfig.save()

# [12/8/09 17:47:51:136 EST] Node
AdminTask.listNodes()

# [12/8/09 17:48:17:170 EST] Nodes
AdminControl.invoke('WebSphere:name=cellSync,process=dmgr,platform=common,node=cell101Manager,version=7.0.0.3,type=CellSync,mbeanIdentifier=cellSync,cell=cell101,spec=1.0', 'syncNode', '[cell101N2]', '[java.lang.String]')

# [12/8/09 17:48:27:638 EST] Nodes
AdminControl.invoke('WebSphere:name=cellSync,process=dmgr,platform=common,node=cell101Manager,version=7.0.0.3,type=CellSync,mbeanIdentifier=cellSync,cell=cell101,spec=1.0', 'syncNode', '[cell101N3]', '[java.lang.String]')

# [12/8/09 17:48:48:536 EST] ApplicationDeployment
#AdminApp.list()

# [12/8/09 17:49:02:927 EST] Enterprise Applications
#AdminControl.invoke('WebSphere:name=ApplicationManager,process=as_cell101a_01,platform=dynamicproxy,node=cell101N2,version=7.0.0.3,type=ApplicationManager,mbeanIdentifier=ApplicationManager,cell=cell101,spec=1.0', 'startApplication', '[DamnSchappettEA]', '[java.lang.String]')

# [12/8/09 17:49:07:200 EST] Enterprise Applications
#AdminControl.invoke('WebSphere:name=ApplicationManager,process=as_cell101a_02,platform=dynamicproxy,node=cell101N3,version=7.0.0.3,type=ApplicationManager,mbeanIdentifier=ApplicationManager,cell=cell101,spec=1.0', 'startApplication', '[DamnSchappettEA]', '[java.lang.String]')



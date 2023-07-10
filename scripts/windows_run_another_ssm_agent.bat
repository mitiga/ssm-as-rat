mkdir C:\tmp\pd
xcopy /Q /E /I C:\ProgramData\Amazon\SSM C:\tmp\pd\Amazon\SSM
rmdir /S /Q C:\tmp\pd\Amazon\SSM\InstanceData
set ProgramData=C:\tmp\pd
"C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe" -register -code <ACTIVATION_CODE> -id <ACTIVATION_ID> -region <REGION> > C:\tmp\register_output.txt
start /B cmd /c "C:\Program Files\Amazon\SSM\amazon-ssm-agent.exe"
timeout 10
start /B cmd /c "C:\Program Files\Amazon\SSM\ssm-agent-worker.exe"

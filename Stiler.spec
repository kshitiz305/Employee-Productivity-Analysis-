# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\Stiler.py'],
             pathex=['C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Executables\\Stiler_8_8'],
             binaries=[],
             datas=[('C:\\Users\\kshitizgupta\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\plotly', 'plotly'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\templates','templates'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\BackupReportTemplate','BackupReportTemplate'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\current_files','current_files'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\DTE&Staffit_templates','DTE&Staffit_templates'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\historical_raw_files','historical_raw_files'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\Latest_Report','Latest_Report'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\Previous_Reports','Previous_Reports'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\ResponseAnalysis','ResponseAnalysis'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\static','static'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\Calendar&Reason.xlsx','.'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\macro.xlsm','.'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\Op_Variance_Data.csv','.'),
			 ('C:\\Users\\kshitizgupta\\Downloads\\Stiler_8_8\\Stiler_8_8\\rstcodes.txt','.')
			 ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Stiler',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Stiler')

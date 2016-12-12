# -*- mode: python -*-

block_cipher = None

a = Analysis(['__main__.py'],
             pathex=[
                 # Path to the project being built
                 '.', '../tuto-file-handling'
             ],
             binaries=None,
             datas=[('./ui/*.ui', 'ui/'),
                    ('./res/*', 'res/'),
                    ('./i18n/*', 'i18n/')],
             hiddenimports=['PySide.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='plustutocenter',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=exe.name)

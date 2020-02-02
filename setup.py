from distutils.core import setup
setup(
  name = 'sentence_diff',         
  packages = ['sentence_diff'],  
  version = '0.1', 
  license='MIT',       
  description = 'Difference English sentences via Liechtenstein distance, calculate word error rate, and list out word by word differences',   
  author = 'Miles Thompson',
  author_email = 'utunga@gmail.com',      
  url = 'https://github.com/utunga/sentence_diff',   
  download_url = 'https://github.com/utunga/sentence_diff/archive/v_01.tar.gz',   
  keywords = ['Levenshtein', 'English', 'Text', 'WER', 'Diff'],   
  install_requires=[            
          'numpy',
          'inflect',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',    
    'Intended Audience :: Developers',   
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3',  
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
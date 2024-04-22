# �����ĵ�

## ����

��ȡ����ƽ̨�й�������ָ���ֶ�����

### �ɼ����ݸ�ʽ

```json
{
  "link": "",
  "title": "",
  "editor": "",
  "state": "",
  "date": "",
  "tax_type": "",
  "text": "",
  "appendix": "",
  "related_documents": ""
}
```

- link ����
- title ����
- editor �ĺ�
- state ״̬
- issue date ��������
- tax type ˰��
- text ����
- appendix �������������أ� ע���������ʱʹ�� ` /` �ֺŷָ�
- related documents ����ļ������ӣ� ע���������ʱʹ�� ` /` �ֺŷָ�

## ����ָ��

### ��������

> ����Ŀʹ�� `poetry` ������������
>
> ������������¼�� [pyproject.toml](..%2Fpyproject.toml) �ļ���
>
>����Ŀ��Ŀ¼��ִ��
>
> ```bash
> # ��ϵͳ�����а�װ  `poetry` ��
> pip install -U poetry 
> # ��װ��������
> poetry install
> # ���� poetry ���������� python ����
> poetry shell
> # ע������Ŀ������ʹ���� playwright ������Զ������ߣ����� playwright �����������
> # ��Ҫʱ���ֶ� `playwright install` ��װ���������
> ``` 

- ����Ϊֹ����Ŀ������������ȫ����װ���

### ��̬����

> ����Ŀʹ�� `dynaconf` ��ʵ�ֶ�̬����

���ز���ʱ������ʹ��ʹ�ñ������ã��滻��ĿĬ�����ã�
���÷������£�
- �ɰ��� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  �ļ���ʽ������ͬ�������� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  ͬ��·�������� `settings.local.yml` �ļ�
- `settings.local.yml` �ļ����Զ��滻�� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  ��Ĭ�����ã����һᱻ `git ignore` ���ᱻ git �ύ��Զ�ֿ̲�
- 

## ʹ��ָ��

```bash
python .\src\crawlers_tax_policy_data\cmdline.py
Usage: cmdline.py [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version  Show version and exit.
  -v, --verbose  Get detailed output
  --help         Show this message and exit.

Commands:
  crawlers-gov  ������վ���棬��ʹ�� `crawlers_gov --help` ��ȡ��ϸ˵��
```
```bash
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov --help

Usage: cmdline.py crawlers-gov [OPTIONS]

  ������վ���棬��ʹ�� `crawlers-gov --help` ��ȡ��ϸ˵��

  �����ǿ��ṩ�Ĳɼ������� ��ʹ�� -c �� --city ����ָ�����棬���� config/settings `CRAWLERS_DATE`
  ��������Ҫ�ɼ�������

  ----------------------------------------------------------------

  gov [������������](www.gov.cn/zhengce/xxgk/)

  ----------------------------------------------------------------

Options:
  -c, --city TEXT  ѡ��Ҫ�ɼ�����վ  [default: gov]
  --help           Show this message and exit.
```

���磺
```bash
# �ɼ� [������������](www.gov.cn/zhengce/xxgk/) ��վ����
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov -c gov
```



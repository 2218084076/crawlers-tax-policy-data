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
- appendix �������������أ� ע: �������ʱʹ�� ` /` �ֺŷָ�
- related documents ����ļ������ӣ� ע: �������ʱʹ�� ` /` �ֺŷָ�

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
> # ע: ����Ŀ������ʹ���� playwright ������Զ�������, ���� playwright ���������, 
> # ��Ҫʱ���ֶ� `playwright install` ��װ���������
> ``` 

- ����Ϊֹ, ��Ŀ������������ȫ����װ���

### ��̬����

> ����Ŀʹ�� `dynaconf` ��ʵ�ֶ�̬����

���ز���ʱ, ����ʹ��ʹ�ñ�������, �滻��ĿĬ������,
���÷�������:

- �ɰ��� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  �ļ���ʽ, ����ͬ�������� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  ͬ��·�������� `settings.local.yml` �ļ�
- `settings.local.yml` �ļ����Զ��滻�� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  ��Ĭ������, ���һᱻ `git ignore` ���ᱻ git �ύ��Զ�ֿ̲�
-

## ʹ��ָ��

- **��������ǰ��ȷ�� [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml) �����ļ��� `START_DATE`
  �� `END_DATE` �����Ƿ�Ϊ����Ҫ�ɼ�������**
- Ĭ�� `START_DATE` �� `END_DATE` ��������Ϊ��, ��Ϊ�ӵ�ǰ���ڿ�ʼ�ɼ�,
  ����˵�����£�

```yaml
# ��Ҫ�ɼ������ڣ�
# ע�����ڸ�ʽҪ���� `������` ����ʽ ���� `20240409` �������Ѷ����˹̶��� date �����߼�
# ����ʾ����2024-01-12��2024��1��2��
# Ҫ��ָ���ɼ�ĳ�쵥�յ����ݣ���ֻ��ָ�� start_date ���� end_date
# start_date �� end_date ������Ϊ�գ����Զ��ɼ���ǰ����������
```

```bash
python .\src\crawlers_tax_policy_data\cmdline.py
Usage: cmdline.py [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version  Show version and exit.
  -v, --verbose  Get detailed output
  --help         Show this message and exit.

Commands:
  crawlers-gov  ������վ����, ��ʹ�� `crawlers_gov --help` ��ȡ��ϸ˵��
```

```bash
Usage: cmdline.py crawlers-gov [OPTIONS]

  ������վ����,��ʹ�� `crawlers-gov --help` ��ȡ��ϸ˵��

  �����ǿ��ṩ�Ĳɼ������� ��ʹ�� -c �� --city ����ָ������,

  ���� config/settings `START_DATE`��`END_DATE` ��ȷ����Ҫ�ɼ�������,Ĭ�ϲɼ����յ�����

  ----------------------------------------------------------------

  gov [������������](www.gov.cn)

  sz-gov [������������](www.sz.gov.cn)

  sh-gov [�Ϻ�����������](www.shanghai.gov.cn)

  zj-gov [�㽭ʡ��������](www.zj.gov.cn)
  ----------------------------------------------------------------

Options:
  -c, --city TEXT  ѡ��Ҫ�ɼ�����վ  [default: gov]
  --help           Show this message and exit.

```

����:

```bash
# �ɼ� [������������](www.gov.cn/zhengce/xxgk/) ��վ����
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov -c gov
```



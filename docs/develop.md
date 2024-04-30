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
- appendix �������������أ�
- related documents ����ļ������ӣ�

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
- ��� `������` www.mof.gov.cn
  ���棬��������ҳ������߼�ͨ�ã���ͨ�� [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  �е� `MOF_URL_SUFFIX` ����ָ��������������
    - ��Ҫ�뵥��������һ����վ������ע�͵�����������վ�����ã�ȫ����ʱ����������βɼ�ָ�����ڷ�Χ�����ݡ�
    - ```yaml
       MOF_URL_SUFFIX:
          �����ĸ�: "/caizhengwengao/index"  # �����ĸ�
          ��������: "/bulinggonggao/czbl/index"  # ��������
          ����������: "/bulinggonggao/czbgg/index"  # ����������
    ```

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
  crawlers-gov  ������վ����, ��ʹ�� `crawlers-gov --help` ��ȡ��ϸ˵��
  run-all       ��һ����ÿ������, ���������ļ���ȷ�ϲɼ�����! 

```

```bash
Usage: cmdline.py crawlers-gov [OPTIONS]

  ������վ���棬��ʹ�� `crawlers-gov --help` ��ȡ��ϸ˵��

  �����ǿ��ṩ�Ĳɼ������� ��ʹ�� -c �� --city ����ָ�����棬

  ���� config/settings `START_DATE`��`END_DATE` ��ȷ����Ҫ�ɼ������ڣ�Ĭ�ϲɼ����յ�����

  ----------------------------------------------------------------
  gov [������������](www.gov.cn)

  sz-gov [������������](www.sz.gov.cn)

  sh-gov [�Ϻ�����������](www.shanghai.gov.cn)

  zj-gov [�㽭ʡ��������](www.zj.gov.cn)

  gd-gov-latest-policy [�㶫ʡ���� > ��������](www.gd.gov.cn/gdywdt)

  gd-gov-doc-lib [�㶫ʡ���� > �ļ���](www.gd.gov.cn/zwgk/wjk/qbwj/)

  gz-gov [�����������淶���ļ�ͳһ����ƽ̨](www.gz.gov.cn/gfxwj/)

  js-gov [����ʡ��������](jiangsu.gov.cn)

  bj-gov [��������������](beijing.gov.cn)

  sc-gov [�Ĵ�ʡ��������](sc.gov.cn)

  safe [�����������](safe.gov.cn)

  mof [������ �����ĸ�;��������;����������](mof.gov.cn)
  ----------------------------------------------------------------

Options:
  -c, --city TEXT  ѡ��Ҫ�ɼ�����վ  [default: gov]
  --help           Show this message and exit.
```

����:

```bash
# �ɼ� [������������](www.gov.cn/zhengce/xxgk/) ��վ����
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov -c gov
# ��һ����ÿ������
python .\src\crawlers_tax_policy_data\cmdline.py run-all
```





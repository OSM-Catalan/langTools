import click
import lib.LangToolsOSM as lt
import re
from tqdm import tqdm


@click.command()
@click.option("--verbose", default=False, is_flag=True)
@click.option("--dry-run", default=False, is_flag=True)
def regex_name_langcommand(verbose, dry_run):
    if not dry_run:
        api = lt.login_OSM()
    area = input("Bounding box(South,West,North,East) or name value: ")
    lang = input("Name language to add (e.g. ca, en, ...): ") or "ca"
    find = input("Regular expression to search at name tags: ")
    replace = input(f"Regular expression to replace object name and fill name:{lang} : ")
    changeset_tags = {u"comment": f"Fill empty name:{lang} tags with regex name:«" +
                                  find + f"» -> name:{lang}=«" + replace + "».",
                      u"source": u"name tag"}
    if verbose:
        print(changeset_tags)
    result = lt.get_overpass_result(area=area, filters=f'nwr["name"~"{find}"][!"name:{lang}"]')
    regex = re.compile(find, )
    changeset = None
    for rn in tqdm(result.nodes):
        if "name" in rn.tags:
            tags = {}
            tags["name:" + lang] = regex.sub(replace, rn.tags["name"])

            if tags:
                lt.print_element(rn, verbose=verbose)
                if changeset is None and not dry_run:
                    api.ChangesetCreate(changeset_tags)
                    changeset = True

                if not dry_run:
                    lt.update_element(element=rn, tags=tags, api=api)

    for rw in tqdm(result.ways):
        if "name" in rw.tags:
            tags = {}
            tags["name:" + lang] = regex.sub(replace, rw.tags["name"])

            if tags:
                lt.print_element(rw, verbose=verbose)
                if changeset is None and not dry_run:
                    api.ChangesetCreate(changeset_tags)
                    changeset = True

                if not dry_run:
                    lt.update_element(element=rw, tags=tags, api=api)

    for rr in tqdm(result.relations):
        if "name:" in rr.tags:
            tags = {}
            tags["name:" + lang] = regex.sub(replace, rr.tags["name"])

            if tags:
                lt.print_element(rr, verbose=verbose)
                if changeset is None and not dry_run:
                    api.ChangesetCreate(changeset_tags)
                    changeset = True

                if not dry_run:
                    lt.update_element(element=rr, tags=tags, api=api)

    if changeset and not dry_run:
        api.ChangesetClose()

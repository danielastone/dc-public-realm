from __future__ import annotations
import html


def esc(x): return html.escape(str(x), quote=True)


def render_overview(o, assertions, entities):
    oid=o['object_entity_id']
    def refs(field):
        raw=(o.get('assertion_refs') or {}).get(field)
        ids=raw if isinstance(raw,list) else ([raw] if raw else [])
        if not ids: raise ValueError(f'{oid}.{field}: displayed fact has no assertion reference')
        missing=[x for x in ids if x not in assertions]
        if missing: raise ValueError(f'{oid}.{field}: missing canonical assertions {missing}')
        return ids
    def require_subject(field,subject):
        ids=refs(field)
        if any(assertions[x].get('subject_id')!=subject for x in ids): raise ValueError(f'{oid}.{field}: assertion subject mismatch')
        return ids
    def attr(ids): return esc(','.join(ids))
    def fact(field,label,value,url):
        ids=require_subject(field,oid)
        if len(ids)!=1 or assertions[ids[0]].get('literal_value')!=value: raise ValueError(f'{oid}.{field}: displayed value does not reconcile to canonical assertion')
        return f'<div data-assertion-ids="{attr(ids)}"><dt>{esc(label)}</dt><dd>{esc(value)} <a class="overview-source" href="{esc(url)}" aria-label="Source for {esc(label)}">Source</a></dd></div>'
    if oid not in entities: raise ValueError(f'{oid}: overview object is not a canonical entity')
    if not all(o.get(k) for k in ('image_url','image_alt','image_credit','image_rights','image_source_url')): raise ValueError(f'{oid}: incomplete image rights metadata')
    rights=esc(o['image_rights'])
    if o.get('image_license_url'): rights=f'<a href="{esc(o["image_license_url"])}">{rights}</a>'
    figure=f'<figure class="record-photo"><img src="{esc(o["image_url"])}" alt="{esc(o["image_alt"])}" loading="eager"><figcaption>{esc(o["image_credit"])} · {rights} · <a href="{esc(o["image_source_url"])}">Image record</a></figcaption></figure>'
    facts=fact('location','Location',o['location'],o['location_source_url'])+fact('event_date',o['event_label'],o['event_date'],o['event_source_url'])
    if o.get('secondary_event_label'): facts+=fact('secondary_event_date',o['secondary_event_label'],o['secondary_event_date'],o['secondary_event_source_url'])
    if o['record_type']=='person_memorial':
        date_ids=refs('subject_dates'); subjects={assertions[x].get('subject_id') for x in date_ids}
        if len(subjects)!=1: raise ValueError(f'{oid}.subject_dates: assertion subjects disagree')
        sid=next(iter(subjects)); person=entities.get(sid)
        if not person or person.get('entity_type')!='Person' or person.get('canonical_name')!=o['subject_name']: raise ValueError(f'{oid}.subject_name: does not reconcile to canonical person')
        if len(date_ids)!=2: raise ValueError(f'{oid}.subject_dates: expected birth and death assertions')
        dates='–'.join(assertions[x].get('literal_value','') for x in date_ids)
        if dates!=o['subject_dates']: raise ValueError(f'{oid}.subject_dates: does not reconcile to canonical assertions')
        bio_ids=require_subject('subject_bio',sid)
        facts+=f'<div data-assertion-ids="{attr(date_ids)}"><dt>Subject</dt><dd><strong>{esc(person["canonical_name"])}</strong> ({esc(dates)})</dd></div>'
        intro=f'<section class="record-introduction" data-assertion-ids="{attr(bio_ids)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the memorial</h2><p>{esc(o["subject_bio"])} <a class="overview-source" href="{esc(o["subject_source_url"])}">Source</a></p></section>'
    elif o['record_type']=='historical_object':
        ids=require_subject('object_context',oid)
        intro=f'<section class="record-introduction" data-assertion-ids="{attr(ids)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the object</h2><p>{esc(o["object_context"])} <a class="overview-source" href="{esc(o["object_context_source_url"])}">Source</a></p></section>'
    else: raise ValueError(f'{oid}: unknown record_type {o["record_type"]}')
    return f'<section class="record-overview" data-object-entity-id="{esc(oid)}" aria-label="Object overview">{figure}<div class="record-facts"><dl>{facts}</dl>{intro}</div></section>'


OVERVIEW_CSS='''.record-overview{display:grid;grid-template-columns:minmax(240px,42%) 1fr;gap:1.5rem;margin:1.4rem 0 2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--line)}.record-photo{margin:0}.record-photo img{display:block;width:100%;height:auto;max-height:430px;object-fit:cover;background:var(--soft)}.record-photo figcaption{margin-top:.45rem;font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.72rem;line-height:1.4}.record-facts dl{margin:0}.record-facts dl>div{display:grid;grid-template-columns:6rem 1fr;gap:.65rem;padding:.55rem 0;border-bottom:1px solid var(--line)}.record-facts dt{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700;color:var(--muted)}.record-facts dd{margin:0}.record-introduction{margin:1.2rem 0 0;max-width:40rem}.record-introduction h2{margin:0 0 .45rem;font-size:1.05rem}.record-introduction p{margin:0}.overview-source{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.7rem;white-space:nowrap}@media(max-width:600px){.record-overview{grid-template-columns:1fr;gap:1rem}.record-photo img{max-height:none}.record-facts dl>div{grid-template-columns:5.4rem 1fr}}'''

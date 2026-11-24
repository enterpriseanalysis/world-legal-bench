"""Reporting groups referencing UN Statistics Division M49 (2026-11-24)."""
REGIONS = {
    'Americas': ('US', 'CA', 'BR', 'MX'),
    'Asia': ('KR', 'CN', 'JP', 'IN', 'ID'),
    'Europe': ('FR',),
    'Africa': ('ZA',),
    'Oceania': ('AU',),
}
COUNTRY_REGION = {country: region for region, countries in REGIONS.items() for country in countries}
M49_SOURCE = 'https://unstats.un.org/unsd/methodology/m49/'
M49_CODES = {'Americas':'019', 'Asia':'142', 'Europe':'150', 'Africa':'002', 'Oceania':'009'}


def regional_summary(by_country, *, complete):
    """Pool items within a region; weight the five regional accuracies equally."""
    rows = []
    for region, countries in REGIONS.items():
        selected = [row for row in by_country if row['country'] in countries]
        if not selected:
            continue
        row = {'region': region, 'm49_code': M49_CODES[region]}
        for key in ('total','submitted','correct','incorrect','invalid','missing','inference_errors'):
            row[key] = sum(item[key] for item in selected)
        row['accuracy'] = 100 * row['correct'] / row['submitted'] if row['submitted'] else None
        rows.append(row)
    macro = sum(row['accuracy'] for row in rows) / 5 if complete and len(rows)==5 else None
    return {'by_region': rows, 'region_macro_accuracy': macro,
            'geographic_grouping': 'UN M49 referenced; selected jurisdictions only'}

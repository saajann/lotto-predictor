def calc_ritardatari(df, ruota='Nazionale'):
    last_extraction = df[df['ruota'] == ruota].iloc[-1]
    return [n for n in range(1,91) if n not in last_extraction.values]
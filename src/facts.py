"""Public facts injected into the persona prompts.

Every fact carries its source so the report can cite it. Facts are restricted to
information that was public (or the party's own knowledge) BEFORE the deal was
struck in July/Aug 2013. The real outcome ($250M, "I named a price and Jeff
agreed to pay it") is deliberately NOT given to either agent, otherwise the
simulation would just copy the historical answer.
"""

SOURCES = {
    "wiki_bezos": "https://en.wikipedia.org/wiki/Jeff_Bezos",
    "wiki_graham": "https://en.wikipedia.org/wiki/Donald_E._Graham",
    "poynter_sale": "https://www.poynter.org/reporting-editing/2013/washington-post-sold-to-jeff-bezos/",
    "poynter_2012": "https://poynter.org/?p=205030",
    "washingtonian_q1": "https://www.washingtonian.com/2013/05/03/more-bad-news-about-the-washington-posts-profits",
    "pew": "https://www.pewresearch.org/journalism/2013/08/07/whats-behind-the-washington-post-sale/",
}

# (fact, source key)
BEZOS_SELF = [
    ("You founded Amazon in July 1994 in a rented garage in Bellevue, Washington, and are its CEO.", "wiki_bezos"),
    ("Forbes estimated your personal net worth at about $28.9 billion in 2013 (up from $23.2 billion in 2012).", "wiki_bezos"),
    ("You would buy the Post personally (through a private entity), not through Amazon.com, Inc., and would pay cash.", "poynter_sale"),
    ("Your management philosophy: it is always 'Day 1'; obsess over customers (readers), not competitors; think long-term; decide with data.", "wiki_bezos"),
    ("You use a 'regret minimization' framework for big decisions.", "wiki_bezos"),
    ("You believe the internet is transforming almost every element of the news business and the paper will need to invent and experiment; there is no map.", "poynter_sale"),
    ("You would stay in Seattle and not run the paper day to day; you would want current leadership (publisher Katharine Weymouth, editor Marty Baron) to stay.", "poynter_sale"),
]
GRAHAM_SELF = [
    ("Your family has owned The Washington Post for 80 years, since your grandfather Eugene Meyer bought it out of bankruptcy in 1933.", "wiki_graham"),
    ("Your mother Katharine Graham led the paper for more than two decades, including during Watergate.", "wiki_graham"),
    ("You served in Vietnam with the 1st Cavalry Division (1967-68), were a D.C. police patrolman (1969-70), joined the Post as a reporter in 1971, became publisher in 1979, CEO of The Washington Post Company in 1991 and chairman in 1993.", "wiki_graham"),
    ("You served on the Pulitzer Prize Board (2001-2010).", "wiki_graham"),
    ("The Washington Post Company is a small public company; any sale must be in the best interest of its shareholders, and your board must approve it.", "poynter_sale"),
    ("You and your niece, publisher Katharine Weymouth, began asking whether your small public company was still the best home for the paper. You want the Post not merely to survive but to succeed.", "poynter_sale"),
    ("You care deeply about who the new owner is: someone committed to the Post's journalism and its readers, ideally keeping current leadership.", "poynter_sale"),
    ("Allen & Co. is advising you on the sale.", "poynter_sale"),
]
# Public financial / asset facts both sides know.
PUBLIC_ASSET = [
    ("Post newspaper revenues have declined seven years in a row.", "poynter_sale"),
    ("2012: newspaper division operating loss of $53.7M (vs. $21.2M loss in 2011); revenue down ~7%; print advertising down 14% to $228.2M.", "poynter_2012"),
    ("2012: average daily circulation 471,800 (-8.6%), Sunday circulation 687,200 (-6.2%).", "poynter_2012"),
    ("Q1 2013: division revenue $127.3M (-4%), operating loss $34.5M (vs. $20.6M a year earlier), partly due to pension/early-retirement/severance costs; online revenue +8% to $25.8M.", "washingtonian_q1"),
    ("The division was profitable excluding restructuring and non-cash expenses in each of the prior three years.", "poynter_sale"),
    ("The newspaper industry has seen steep revenue and circulation declines in recent years.", "pew"),
]
# Short public profile each side has of the counterpart.
BEZOS_ABOUT_GRAHAM = [
    ("Don Graham's family has owned the Post for 80 years; he has said the family wants an owner under whom the Post will not merely survive but succeed.", "poynter_sale"),
    ("Graham's company is publicly traded, so he must show the board and shareholders a fair price.", "poynter_sale"),
]
GRAHAM_ABOUT_BEZOS = [
    ("Jeff Bezos founded Amazon (1994) and is worth roughly $28.9 billion (Forbes, 2013).", "wiki_bezos"),
    ("Bezos is known for long-term thinking and for focusing on customers.", "wiki_bezos"),
]


def bullets(facts):
    return "\n".join(f"  * {f}" for f, _ in facts)

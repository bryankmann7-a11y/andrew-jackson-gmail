"""Conservative name repair and editorially labelled reading aids for OCR letters.

Nothing replaces or silently edits original OCR. No adaptation is presented as a
verbatim quotation or as checked against a manuscript scan.
"""
import datetime as dt
import re
from collections import defaultdict

# Each modernization is a hand-edited, condensed rendition checked against
# the *OCR passage* in the public-domain Bassett edition, not against originals.
# It may omit detail and it is not a diplomatic transcript.
EARLY = {
'1788-08-12|Waightstill Avery': """Sir,

When a man's character and feelings have been injured, he ought to seek a quick remedy. You received a few lines from me yesterday and surely understood what I meant. You have damaged my reputation and insulted me before a court and a large audience. I therefore call upon you, as a gentleman, to give me satisfaction for that insult.

I expect an immediate, unambiguous answer. I hope you can go without dinner until this is settled. When a gentleman injures another man, he should make matters right promptly. I expect you to meet me today.

Your obedient servant,

Postscript: This evening, after court adjourns.""",
'1789-02-13|Daniel Smith': """Sir,

Yesterday I met Captain Fargo, who asked me to visit you today. The gloomy weather prevents me, so I am sending his request in writing.

He says he is concerned for this country's welfare and peace. He hopes to become a citizen and trade here. I believe that, with your help, his proposed trade could lead to lasting peace with the Indians.

He wants you to write to the Spanish governor about a commercial agreement. Fargo would then ask the governor for permission to trade here, which he expects to receive because they are related. He could explain how peace would help trade and remind the governor that the district was named in his honor.

Fargo holds a captain's commission from the King of Spain. I believe he could do considerable good for this region. Please meet him before he leaves for New Orleans, because I believe this is our most immediate opportunity for peace.

Consider the proposal and send me your thoughts through Colonel Donelson, who carries this letter. I care about the welfare of this country. And if you travel to see Fargo, please call on me; I believe I can offer further useful information.

Your humble servant.""",
'1791-01-20|Daniel Smith': """Sir,

David Allison has given me power of attorney to handle business for Barnard's heirs, including supervision of surveys of their land claims.

I asked Anthony Foster, whom I understood you had deputized for surveys, to do the work. I waited eight days, but he would not survey along the cardinal directions as I believed the law required. On the ninth day, Major Hay agreed to survey the land with Foster present. He will return the survey if you grant him special authority.

The heirs have been kept from the profits of their land for years. I cannot understand why Foster refused. He had been willing to begin, but his proposed bearings and boundaries seemed unlawful to me. I set the compass myself and established a line due north toward the river, which I believe accords with our laws.

Given these circumstances, please authorize Major Hay to submit his survey. You can send the authorization through Captain William Donelson or Mr. Hayne, who carries this letter.

Your obedient and humble servant.""",
'1793-01-30|John McKee': """Dear Sir,

I received your letter by Mr. Russell and understand that, on Governor Blount's advice, my papers were not sent by the first express. Whatever you and the governor decide about my business is satisfactory to me. Experience tells me that both of you have my interests at heart, so I leave the timing and the proper authentication of the papers to your judgment.

The announcement of peace on our western frontier, followed by attacks and killings, has caused great anger here. I fear the Indians may have used the peace announcement to lull settlers into a false sense of security, protect their own towns, and make attacks easier. Since that announcement, at least twelve people in this district have been killed or wounded.

Why are we attempting another treaty? Have they observed the last one? I believe they have not. Why negotiate with people who, in my view, will not honor treaties or the accepted law of nations? I would appreciate your opinion on these questions in your next letter.

With the highest esteem, your obedient servant.""",
'1794-05-16|John McKee': """Dear Sir,

Your letter of April 17 gave me strong hopes for general peace with the southern Indians. But scarcely had I finished reading it when I learned that another man had been murdered. Since then, attacks on the frontier have continued, and my hopes have disappeared.

I fear that the peace talks are intended to mislead us and make us less watchful. In my view, treaties have made it easier for attackers to enter settlements. I do not understand Congress's continuing preference for negotiation. Some say humanity requires it, but humanity ought to extend equally to American citizens.

Our own citizens have been prosecuted for marching into Native towns and killing people. Why should we not demand, under the treaty, that the murderers of our citizens be surrendered? If they are not given up, I regard that as a violation of the treaty and grounds for war. In my opinion, a nation that refuses to surrender the perpetrators should share responsibility for the crime.

I dread the coming summer. Frontier settlers are discouraged, and some are leaving for Kentucky. Unless Congress offers better protection, I fear the country will weaken or seek protection from another power.

Please send news from your area. I will write more in my next letter.

Your humble servant.""",
'1795-06-09|John Overton': """Dear Sir,

I expected to see you in Knoxville yesterday, because I had urgent business to settle and $2,500 depended on my getting there promptly. I am surprised you did not ride over to hear how my long, expensive journey turned out. You may appear unconcerned, but I imagine you still want to know about our business.

I traveled through North Carolina and then to Frederick Town without accomplishing what I had hoped. In Philadelphia, where I expected simply to sign the papers and collect the money, almost nothing was ready. After twenty-two days of difficulty I finally arranged a sale of the land to David Allison at one-fifth of a dollar per acre, on shorter credit than had first been proposed.

A lawyer then challenged the title to 1,000 acres because the deeds did not establish Elisha Rice's authority over land originally granted to John Rice. I was in a dreadful position. I had to agree to correct the titles. Governor Blount has the papers for your inspection, and I have kept a copy of the agreement.

I have enclosed a financial statement and details about the drafts and payments. We can discuss the remaining accounts and purchases when we meet.

I never want to undertake so troublesome a transaction again, not even for all the land on the Hatchie River. I am exhausted nearly to death and hope to reach home.

Your obedient servant.

[Condensed: complicated payment figures and several business instructions are omitted. Consult Original text for them.]""",
'1795-08-19|William Cupples': """Dear Sir,

About the note you mentioned: as far as I remember, we won five pounds from S. Bittles. I paid my share in cash, and yours was paid with cloth for breeches. You later purchased brown cloth from Mr. Allen for a coat, at about eight pounds. I recall that you and Allen settled accounts at Mr. Lincar's after Anson court, with Mr. Crawford present, and you wrote the note. Crawford witnessed it. The note is in my possession, and I will follow your directions about it.

I was astonished that you came within fifty miles without visiting me. If I had been that near you, little could have kept me away.

Politics here consists mostly of complaints about Jay and his treaty. We have also had destructive flooding, damage to crops, and the prospect of much fever.

I am seriously considering visiting your country. Tell me whether I could support myself by my profession and what settlement land costs and is like. Mr. Collier, who works in my household, may visit your neighborhood and call on you. If he does not, please write at your first opportunity.

More than half my family is sick with fever. My best wishes to you and yours.

[Condensed from the surviving printed OCR.]""",
'1795-10-04|Nathaniel Macon': """Sir,

When I was in Philadelphia last April, David Allison gave me a full account of the matter you had been pursuing for me. I was grateful for the effort you had made. Please continue helping me get a final decision when Congress meets again, and let me know the outcome.

Jay's recent treaty with Britain has put our country in an alarming position. Will it lead to civil war, or will representatives in Congress challenge it? In my opinion it is not a proper reciprocal commercial treaty, and its negotiation and approval have violated constitutional principles.

The Constitution calls for treaties to be made by the president with the Senate's advice and consent. I object that the Senate was not consulted before this one was negotiated, only afterward. I also object to its implications for revenue and to other provisions I believe exceed constitutional authority.

I could say much more, but you understand these issues better than I do. I will leave it there.

With the highest esteem, your obedient servant.

[Condensed from the original letter. This expresses Jackson's arguments, not settled constitutional law.]""",
'1795-12-03|Joseph Anderson': """Dear Sir,

After a difficult ride, I reached home on the first of this month and found my family well. I was especially delighted to learn that a son had been born about ten days earlier. Please give Mrs. Jackson my warm regards and accept my thanks for the kindness you both showed me during my visit.

I am sending a power of attorney through Samuel Donelson. I would like you to inspect 640 acres at the mouth of Cedar Lick Creek, apparently owned by Crutchfield's heirs. Captain Caffery is handling the sale. I trust your judgment about the land, the risk of flooding, the price, and whether the title is sound. If you think it worth the asking price, please buy it for me.

I would prefer to pay next autumn, possibly with horses, cash, or an enslaved person, because I have other land purchases under way. Please also inquire about a tract adjoining Castleman's on Stoner's Creek.

The territory's population appears to entitle it to two congressional representatives. I and others would like to see you and William C. C. Claiborne serve.

[Condensed; the full OCR text continues with other remarks.]""",
}
CANONICAL = [
'Waightstill Avery','Daniel Smith','John McKee','John Overton','William Cupples',
'Nathaniel Macon','Joseph Anderson','Robert Hays','John Sevier','John McNairy',
'William Cocke','John Coffee','Francis P. Blair','Amos Kendall','Andrew J. Donelson',
'Andrew Jackson, Jr','James K. Polk','Martin Van Buren','Thomas Pinckney',
'John H. Eaton','Thomas H. Benton','Edward Livingston','Sam Houston',
'John Armstrong','Willie Blount','Henry Clay','James Buchanan','Andrew Jackson',
'George W. Campbell','Thomas Jefferson','James Monroe','John C. Calhoun',
'William C. C. Claiborne','James Wilkinson','Isaac Shelby','James Madison',
'William H. Crawford',
]
# These represent explicit, checked variants, not guesses about other people.
ALIASES={
 'waicutsttill avery':'Waightstill Avery',
 'joun mckee':'John McKee','jonn mckee':'John McKee','john mckee':'John McKee',
 'joun mcnairy':'John McNairy','joun mcnarry':'John McNairy',
 'john mcnarry':'John McNairy','john mcnatry':'John McNairy',
 'daniel smith':'Daniel Smith','nathaniel macon':'Nathaniel Macon',
 'john overton':'John Overton','robert hays':'Robert Hays',
 'rozpert hays':'Robert Hays','rosert hays':'Robert Hays',
 'john sevier':'John Sevier','joun sevier':'John Sevier','johnn sevier':'John Sevier',
 'joseph anderson':'Joseph Anderson','william cupples':'William Cupples',
 'john coffee':'John Coffee','johnn coffee':'John Coffee','joun coffee':'John Coffee',
 'john h. eaton':'John H. Eaton','joun h. eaton':'John H. Eaton',
 'francis p. blair':'Francis P. Blair','francis p. blarr':'Francis P. Blair',
 'francis p. brarr':'Francis P. Blair','francis p. biarr':'Francis P. Blair',
 'francis p. buarr':'Francis P. Blair','francis p. blatr':'Francis P. Blair',
 'francis p. bair':'Francis P. Blair','francis p. barr':'Francis P. Blair',
 'francis p. bratr':'Francis P. Blair',
 'andrew j. donelson':'Andrew J. Donelson','andrew j. donelson':'Andrew J. Donelson',
 'james k. pork':'James K. Polk','james k. polk':'James K. Polk',
 'thomas pinckney':'Thomas Pinckney','tuomas pinckney':'Thomas Pinckney',
 'thomas h. benton':'Thomas H. Benton','tuomas h. benton':'Thomas H. Benton',
 'edward livingston':'Edward Livingston','epwarp livingston':'Edward Livingston',
 'governor claiborne':'William C. C. Claiborne',
 'president monroe':'James Monroe','secretary monroe':'James Monroe',
 'secretary calhoun':'John C. Calhoun','vice-president calhoun':'John C. Calhoun',
 'vice-president van buren':'Martin Van Buren','secretary van buren':'Martin Van Buren','president van buren':'Martin Van Buren',
 'president polk':'James K. Polk','president tyler':'John Tyler',
 'secretary adams':'John Quincy Adams',
 'postmaster general kendall':'Amos Kendall',
}
TITLES=re.compile(r'^(?:brigadier[\s-]*general|major[\s-]*general|colonel|col|gen|general|rev|reverend|dr|mr|mrs|miss|hon)\.?\s+',re.I)
def key_name(s):
    s=re.sub(r'\s+',' ',str(s).strip())
    s=re.sub(r'[.,;:!?]+$','',s)
    return s.lower().replace('—','-')

def normalize_person(name):
    raw=name.strip()
    if raw=='Andrew Jackson':return raw
    n=re.sub(r'\s+',' ',raw.strip()).title()
    n=re.sub(r'\bJoun\b|\bJonn\b|\bJohnn\b','John',n)
    n=re.sub(r'\bTuomas\b','Thomas',n)
    n=re.sub(r'\bMckee+\b','McKee',n,flags=re.I)
    n=re.sub(r'\bSeviee?r\b','Sevier',n,flags=re.I)
    n=re.sub(r'\bRozpert\b|\bRosert\b','Robert',n)
    n=re.sub(r'\bEpwarp\b','Edward',n)
    n=re.sub(r'\bAnprew\b','Andrew',n)
    n=re.sub(r'\bBlatr\b|\bBlarr\b|\bBiarr\b|\bBrarr\b|\bBuarr\b|\bBair\b','Blair',n)
    t=TITLES.sub('',n)
    n=ALIASES.get(key_name(n),ALIASES.get(key_name(t),n))
    # Explicit role aliases; avoid merging less certain unknowns.
    return n

def reading_copy(s):
    # Presentation only. Original raw OCR stays untouched.
    s=s.replace('\r\n','\n')
    s=re.sub(r'(?<=\w)-\s*\n\s*(?=\w)','',s)
    s=re.sub(r'(?<=[a-z,;])\n(?=[a-z])',' ',s)
    s=re.sub(r'\n\s*\n\s*\n+','\n\n',s)
    return s.strip()

def enrich(letters):
    for d in letters:
        d['ocrFrom']=d['from']
        d['ocrTo']=d['to']
        d['from']=normalize_person(d['from'])
        d['to']=normalize_person(d['to'])
        d['subject']=d['from']+' to '+d['to']+' ('+d['date']+')'
        d['readable']=reading_copy(d['original'])
        d['textQuality']='uncorrected OCR; mechanically reflowed reading copy is not a transcription check'
        other=d['to'] if d['from']=='Andrew Jackson' else d['from']
        key=d['date']+'|'+other
        if key in EARLY:
            d['modern']=EARLY[key]
            d['modernType']='condensed, human-authored rendering checked against printed OCR; not scan-verified'
            d['summary']='Plain-English rendering available; open the Modern English tab. Compare against Original OCR before quoting.'
        else:
            d['modern']=''
            d['modernType']='not yet written'
        d['needsReview']=d.get('needsReview',False) or len(d.get('original',''))>18000
        d['replyToId']=None
        d['replyLinkStatus']='no matched surviving earlier letter identified'
    # Only create conservative *suggested* reply links between opposite-direction
    # letters to the same person within two weeks, with textual reply language.
    previous=defaultdict(list)
    for d in sorted(letters,key=lambda x:(x['date'],x['id'])):
        other=d['to'] if d['from']=='Andrew Jackson' else d['from']
        direction='out' if d['from']=='Andrew Jackson' else 'in'
        inverse='in' if direction=='out' else 'out'
        if re.search(r'(?i)\b(?:your (?:letter|note)|(?:received|recd\.?|receipt of) your letter|in (?:answer|reply) to)\b',d['original'][:1250]):
            possibilities=[]
            for past in previous.get((other,inverse),[])[-8:]:
                gap=(dt.date.fromisoformat(d['date'])-dt.date.fromisoformat(past['date'])).days
                if 0<=gap<=14:possibilities.append((gap,past))
            if len(possibilities)==1:
                d['replyToId']=possibilities[0][1]['id']
                d['replyLinkStatus']='possible reply, date/proximity only; not verified'
        previous[(other,direction)].append(d)
    return letters

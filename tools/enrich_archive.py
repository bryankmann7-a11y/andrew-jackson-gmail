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
# The same-day Jackson/Sevier exchange has two different authors:
# index by sender as well as recipient to avoid putting one man's words in the other's mouth.
DIALOGUE={
 '1797-05-10|Andrew Jackson|John Sevier': """Sir,

I have considered your letter of May 8. I agree with much of what you say about general principles, and I recognize that facts can be misstated.

When I spoke at the militia election, I was neither your political nor your private enemy, and I do not wish to become one. But I must defend my feelings and reputation when they are maliciously injured, just as you would.

I am pleased to believe that you did not intend maliciously to injure my reputation and that your earlier letters were written in anger. I hope you were not driven by party spirit, although seeing Joel Lewis use your private letter in public gave me reason to think otherwise.

I recognize that a governor is answerable for official acts through constitutional procedures. Malicious personal slander, however, is a matter of honor. I hope neither of us has committed it. In the future, please distinguish criticism of your public conduct from a personal attack.

As for Lewis, if he used your letter without permission, that is a matter between him and you.

I would gladly talk with you in person. Please suggest a time when I can visit your room.

[Condensed from the printed OCR; this is Jackson's position, not a literal quotation.]""",
 '1797-05-11|John Sevier|Andrew Jackson': """Sir,

Your polite letter of yesterday deserves an immediate and candid reply. I assure you that I have never regarded you as either a personal or political enemy. I am happy to be friendly with any man of merit.

We both seem to want an honorable reconciliation. If we speak coolly and sincerely, that reconciliation can last.

You propose a personal meeting and ask me to name the time and the people who should attend. I agree. I will stay in town until the court adjourns and can meet wherever you choose. I have no strong preference about those present, but Captain Sparks and Judge Claiborne are with me, and I may ask General Robertson to come as well.

An honorable man should acknowledge a mistake once convinced of it. If either of us has acted rashly, I hope we will make the necessary concessions and end with a real friendship, not merely a polite appearance of one.

Your humble servant.

[Condensed from the printed OCR of Sevier's reply.]""",

 '1797-05-08|Andrew Jackson|John Sevier': """Sir,

Your friendly letters while I was in Philadelphia made me think you understood why I criticized your official conduct at a militia election. I believed I had the right, as a citizen, to express an opinion about a governor's official acts.

Imagine my surprise on returning to learn that, while writing those friendly letters, you had privately referred to me as a petty lawyer whose criticism you despised. I do not think my conduct justified such language.

Here is what happened: I attended the militia officers' election as a private citizen and did not intend to interfere. But Joel Lewis produced a private letter from you in support of the idea that the governor could delegate his constitutional duties. I thought that set a dangerous precedent. I objected sharply and said I regretted having to expose the governor's ignorance on that point. My objection was to the official action, not an attack on your private character.

Why write insulting private letters about me instead of addressing your complaint directly to me? I expect an explanation and redress for the injury to my reputation.

I also wonder whether you authorized Lewis to use your letter to influence that election.

[Condensed from the printed OCR, not verified against the manuscript.]""",
 '1797-05-08|John Sevier|Andrew Jackson': """Sir,

I have received your letter today and will answer it as plainly as I can. I seek peace with others, but I cannot remain silent when my reputation is attacked.

I sent blank commissions for the cavalry officers to General Robertson because I believed it was within my authority, not because I wished to advance a faction. If I violated the Constitution, I am answerable to the proper authorities.

I heard that you had spoken harshly and unfairly about my official conduct. At the time I viewed you as an enemy and used angry language in private letters, including some of the expressions you quote. Later explanations from Robertson and Judge Claiborne softened my resentment, and I concluded that I should not treat you as a personal enemy even if I still disagreed with your criticism.

That is why my letters to you in Philadelphia were friendly. They were not intended as a deception.

My reputation is my greatest treasure after years of public life, and I have worked to earn the confidence of the people of Tennessee. I did not write from malice; I wrote as a man who believed himself injured. I admit that anger can make me less measured, just as it can you.

Your obedient servant.

Postscript: I request an answer.

[Condensed from the printed OCR, not verified against the manuscript.]""",
}

# Hand-edited modern-English summaries of short, identifiable OCR passages.
# These are abbreviated reading aids, not verbatim quotations or scan-verified
# diplomatic transcriptions. Stable IDs refer to *raw* Bassett OCR segments.
EARLY_BY_ID = {
"basset-1-9e869e7885e988a": """Sir,

I received your letter today and am very sorry to hear that Mrs. Jackson has been unwell. I hope she is already recovering. I also regret that you must leave Knoxville so soon, though I understand that the business calling you away is urgent.

Thank you for offering to carry letters for me. If I can prepare a letter to Judge McNairy in time, I will entrust it to you.

I will recommend Mr. Eli Hammond to the Secretary of War. I also intend to mention him personally to the Secretary of State and the President, and I hope the recommendations will succeed.

I have a private matter to discuss with one of the judges. If you can spare about fifteen minutes this evening, I would appreciate speaking with you.

With respect and esteem, your obedient servant.

[Condensed from Sevier's printed letter; unrelated editorial footnotes are omitted.]""",
"basset-1-aa7f6f673d41b47": """Sir,

Your insulting words and conduct toward me yesterday revealed, in my opinion, an arrogant and dishonorable character. I believe your anger came from evidence of fraud against you.

The people have made you governor, and I respect that office, but I do not respect the way you treated me. I demand an explanation and the satisfaction your conduct requires.

My friend will deliver this letter and give you the time and place where I expect you to meet me. Come with one friend and no one else. My friend and I will carry pistols. You cannot misunderstand what I mean.

[Condensed from Jackson's printed OCR. This is an explicit armed challenge, not evidence that a duel actually occurred on this occasion.]""",
"basset-1-32f7d2dac87b636": """Sir,

If you find the saltworks in Illinois can be bought on good terms, you are authorized to sign an agreement in my name to secure payment.

I cannot judge their value precisely, but I think $25,000 paid in merchandise might be a good purchase. If payment can be spread over three to five years, you may consider up to $35,000, although with only three years to pay I would prefer no more than $30,000. These are guidelines rather than strict instructions. Do not exceed $40,000.

If buying is impossible, try to lease the saltworks for ten years on terms you consider suitable. You may sign for me in that arrangement as well.

I want at least a one-third share, or one-half if you prefer that only the two of us be involved. I hope we can meet to discuss the details, and I can then give you fuller authority.

With respect.

[Condensed from the printed OCR. An intervening editorial footnote is omitted.]""",
"basset-1-a05bb0177e766ab": """My love,

I just received your letter of March 24. It pains me deeply to know how distressed you are. I would be happy to return to your arms, ease your worries, and spend our days quietly together away from public life.

Mr. Coffee cannot continue the journey and must turn back. If I came home now, would it truly bring you peace, or could it lead us into poverty? That possibility frightens me.

News from Washington suggests that I might be appointed governor of New Orleans. If that happens, I will return, and Coffee has promised to arrange his affairs and meet me again before we go on toward Philadelphia.

Your letters and Mr. Hutchings's tell me how anxious you are about my safety. I have written by every post since I left and will continue to do so while I travel.

I must stop now because I have been called into court. Before I leave this place, I will write more. I pray that God grants you health and peace of mind until I can hold you again.

Your unchanging Andrew Jackson.

[Condensed modern-English rendering based on the printed OCR, not checked against the manuscript.]""",
"basset-1-14ea21c23102551": """Sir,

If our government or country is insulted or attacked from any direction, I believe the people of Tennessee, especially the men under my command, would be ready to serve.

I therefore offer their services to you. If you accept, I can issue orders at once.

I enclose military orders that I recently issued. I have not yet received complete returns from the volunteer companies, but I believe three regiments of volunteers could be assembled under their own officers and be ready to march within twenty days after receiving orders.

Please accept my high respect.

[Condensed from the printed OCR. This is an offer of service, not proof that the regiments were mobilized.]""",
"basset-1-719ea98a3509ec1": """Dear Sir,

I wrote to you at length by the last mail about a matter on which I have heard nothing further. I remain strongly convinced of my belief, although I cannot yet prove it. Circumstances may still prevent the reported plan from coming to anything.

I have little other news. There is a report that Colonel Burr has been arrested in Frankfort, Kentucky, on a charge of raising men to invade Mexico. I cannot confirm that report, but I consider its source credible.

[Condensed from the printed OCR, which ends in a damaged passage. Jackson reports a rumor, not a confirmed arrest.]""",
"basset-1-3ba8d6b99e16837": """Sir,

Allow me to introduce the bearer, Mr. Seth Pease. He is a confidential agent of the government.

He is traveling to examine whether the mail is being carried properly and on time. He is also investigating reports of a plan supposedly forming along the Ohio River that could threaten the peace of the United States.

Any information you can give him would help your country and oblige me.

Please treat this letter as confidential.

Your obedient servant.

[Condensed from Daniel Smith's printed letter; intervening editorial footnotes are omitted.]""",
"basset-1-540838e26cba234": """Sir,

I have read your letter from today. You explain that the harsh language near its end referred to yourself, not to me. I had understood it differently because people seldom describe their own faults in such severe terms. Your explanation shows that I misunderstood your meaning.

Still, I must speak frankly: the end of our former close friendship continues to hurt me. I do not want to prolong this argument. We can go through life treating each other with the courtesy expected of civilized people, even if the old friendship cannot be restored.

You may have a copy of your letter whenever you wish, as long as I retain it.

Your obedient servant.

[Condensed from the printed OCR; the original letter has not been checked against the scan.]""",
"basset-1-06465203ac3cd4e": """Dear Colonel,

I have written you many letters since leaving home and received no reply. Except for Captain Caffery, none of my friends have written. Please tell me why.

Reports from our commissioners in France are contradictory. We know they were politely received by the foreign minister, but it is unclear whether the French government has officially recognized them. France seems to be preparing an attack on Ireland and England. That might benefit America, though a sudden French peace with Britain could leave our own country vulnerable.

I am sending newspaper debates from Congress and have sent other papers to Nashville. I have not yet made arrangements for our trading business. I am waiting to hear from you and from General Winchester.

Please tell me how the land dispute involving Sandy, Bledsoe's heirs, and Donelson was settled. A treaty with the Cherokees is planned for spring, and the government may purchase land from them. If the Tennessee River becomes a boundary, land along Duck River could become valuable. Hold what you own and consider acquiring more.

Give my respects to your wife.

[Condensed from the printed OCR. Editorial footnotes and some qualifications are omitted.]""",
"basset-1-a440eef6ccfec38": """Sir,

You made a private, confidential letter of mine public and accused me of using it to deceive you. You have also told people that I acted dishonestly toward you in your election to the Senate.

I regard these as serious injuries to my reputation. Your explanation for publishing the letter rests on information that, after investigation, I believe to be false.

I therefore demand that you repair the harm you have done, as a gentleman should, or meet me and give the satisfaction one gentleman owes another for such an insult. The man delivering this letter has authority to act for me in arranging the matter.

Your humble servant.

[Condensed from the printed OCR. The demand for 'satisfaction' is historical language associated with an affair of honor; do not treat this as a verified verbatim quotation.]""",
"basset-1-a52ce575b2cd058": """Dear Sir,

Thank you for your letter carried by Mr. Irwin, and for introducing me to him. I find him an agreeable young man and would gladly show him every courtesy I can.

I am sorry that circumstances prevent me from seeing you at the treaty. I would write more, but time and unpleasant business are pressing upon me.

Please give my warmest regards to your wife. I remember her kindness and courtesy with gratitude.

With great esteem, your obedient servant.

[Condensed from the letter portion of the printed OCR; intervening editorial footnotes are omitted. This is not a scan-verified transcription.]""",
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
 'john overton':'John Overton','john oveertonn':'John Overton','robert hays':'Robert Hays',
 'rozpert hays':'Robert Hays','rosert hays':'Robert Hays',
 'john sevier':'John Sevier','joun sevier':'John Sevier','johnn sevier':'John Sevier',
 'joseph anderson':'Joseph Anderson','william cupples':'William Cupples',
 'john coffee':'John Coffee','johnn coffee':'John Coffee','joun coffee':'John Coffee','jouhn coffee':'John Coffee',
 'john h. eaton':'John H. Eaton','joun h. eaton':'John H. Eaton',
 'francis p. blair':'Francis P. Blair','francis p. blarr':'Francis P. Blair',
 'francis p. brarr':'Francis P. Blair','francis p. biarr':'Francis P. Blair',
 'francis p. buarr':'Francis P. Blair','francis p. blatr':'Francis P. Blair',
 'francis p. bair':'Francis P. Blair','francis p. barr':'Francis P. Blair',
 'francis p. bratr':'Francis P. Blair',
 'andrew j. donelson':'Andrew J. Donelson','andrew j. doneetson':'Andrew J. Donelson','andrew j. donnelson':'Andrew J. Donelson',
 'james k. pork':'James K. Polk','james k. polk':'James K. Polk','james k. porx':'James K. Polk',
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
# These noisy headings all explicitly say '... B. Lewis' and differ only in
# OCR spellings of William/Lewis and rank; do not apply fuzzy name matching.
WILLIAM_LEWIS_HEADING=re.compile(r'(?i)^(?:(?:major|mayor)\s+)?w[ilutxr.]{2,12}a{1,2}m{1,2}\s+b[.,]?\s+lew[iyt]+s$')
def key_name(s):
    s=re.sub(r'\s+',' ',str(s).strip())
    s=re.sub(r'[.,;:!?]+$','',s)
    return s.lower().replace('—','-')

def normalize_person(name):
    raw=name.strip()
    if raw=='Andrew Jackson':return raw
    n=re.sub(r'\s+',' ',raw.strip()).title()
    if WILLIAM_LEWIS_HEADING.fullmatch(n):return 'William B. Lewis'
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
    for canonical in CANONICAL:
        if key_name(n)==key_name(canonical):return canonical
    return n

def reading_copy(s):
    # Original OCR is retained in the 'original' field, byte-for-byte.
    from clean_ocr import clean_ocr_text
    return clean_ocr_text(s)

def enrich(letters):
    for d in letters:
        d['ocrFrom']=d['from']
        d['ocrTo']=d['to']
        d['from']=normalize_person(d['from'])
        d['to']=normalize_person(d['to'])
        d['subject']=d['from']+' to '+d['to']+' ('+d['date']+')'
        d['readable']=reading_copy(d['original'])
        d['textQuality']='uncorrected OCR; page furniture removed and suspicious spans flagged in reading copy, not checked against scan'
        d['ocrUnclearSpans']=d['readable'].count('[unclear OCR]')
        from ocr_audit import audit_letter
        d['ocrFlags']=audit_letter(d)
        d['needsReview']=d.get('needsReview',False) or bool(d['ocrFlags'])
        other=d['to'] if d['from']=='Andrew Jackson' else d['from']
        key=d['date']+'|'+other
        dialogue=d['date']+'|'+d['from']+'|'+d['to']
        if d['id'] in EARLY_BY_ID:
            d['modern']=EARLY_BY_ID[d['id']]
            d['modernType']='condensed, human-authored rendering checked against printed OCR; not scan-verified'
            d['summary']='Plain-English rendering available; compare it with Original OCR before quoting.'
        elif dialogue in DIALOGUE:
            d['modern']=DIALOGUE[dialogue]
            d['modernType']='condensed, human-authored rendering checked against printed OCR; not scan-verified'
            d['summary']='Plain-English correspondence rendering available, with original OCR alongside it.'
        elif key in EARLY:
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

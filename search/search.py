from __future__ import print_function, unicode_literals

import sys
import pdb
import re

import apsw
import ctypes
import struct
import sqlitefts as fts
from nltk.tokenize.punkt import PunktLanguageVars
from cltk.tokenize.word import WordTokenizer
from nltk.tokenize import WhitespaceTokenizer


#latin tokenizer from cltk that has been updated to be compatible with the sql-fts-wrapper.
class OUWordTokenizer(fts.Tokenizer):  # pylint: disable=too-few-public-methods
    """Tokenize according to rules specific to a given language."""

    def __init__(self, language):
        """Take language as argument to the class. Check availability and
        setup class variables."""
        self.language = language
        self.available_languages = ['latin']
        assert self.language in self.available_languages, \
            "Specific tokenizer not available for '{0}'. Only available for: '{1}'.".format(self.language,  # pylint: disable=line-too-long
                                                                                            self.available_languages)  # pylint: disable=line-too-long

        if self.language == 'latin':
            self.enclitics = ['que', 'ne', 'ue', 've', 'cum','st']

            self.inclusions = []
            
            cum_inclusions = ['mecum', 'tecum', 'secum', 'nobiscum', 'vobiscum', 'quocum', 'quicum' 'quibuscum']
            
            self.exceptions = self.enclitics

            que_exceptions = []
            ne_exceptions = []
            ue_exceptions = []
            ve_exceptions = []
            cum_exceptions = []
            st_exceptions = []

            # quisque
            que_exceptions += ['quisque', 'quidque', 'quicque', 'quodque', 'cuiusque', 'cuique',
                               'quemque', 'quoque', 'quique', 'quaeque', 'quorumque', 'quarumque',
                               'quibusque', 'quosque', 'quasque']

            # uterque
            que_exceptions += ['uterque', 'utraque', 'utrumque', 'utriusque', 'utrique', 'utrumque',
                               'utramque', 'utroque', 'utraque', 'utrique', 'utraeque', 'utrorumque',
                               'utrarumque', 'utrisque', 'utrosque', 'utrasque']

            # quiscumque
            que_exceptions += ['quicumque', 'quidcumque', 'quodcumque', 'cuiuscumque', 'cuicumque',
                               'quemcumque', 'quamcumque', 'quocumque', 'quacumque', 'quicumque',
                               'quaecumque', 'quorumcumque', 'quarumcumque', 'quibuscumque',
                               'quoscumque', 'quascumque']

            # unuscumque
            que_exceptions += ['unusquisque', 'unaquaeque', 'unumquodque', 'unumquidque',
                               'uniuscuiusque', 'unicuique', 'unumquemque', 'unamquamque', 'unoquoque',
                               'unaquaque']

            # plerusque
            que_exceptions += ['plerusque', 'pleraque', 'plerumque', 'plerique', 'pleraeque',
                               'pleroque', 'pleramque', 'plerorumque', 'plerarumque', 'plerisque',
                               'plerosque', 'plerasque']

            # misc
            que_exceptions += ['absque', 'abusque', 'adaeque', 'adusque', 'aeque', 'antique', 'atque',
                               'circumundique', 'conseque', 'cumque', 'cunque', 'denique', 'deque',
                               'donique', 'hucusque', 'inique', 'inseque', 'itaque', 'longinque',
                               'namque', 'oblique', 'peraeque', 'praecoque', 'propinque',
                               'qualiscumque', 'quandocumque', 'quandoque', 'quantuluscumque',
                               'quantumcumque', 'quantuscumque', 'quinque', 'quocumque',
                               'quomodocumque', 'quomque', 'quotacumque', 'quotcumque',
                               'quotienscumque', 'quotiensque', 'quotusquisque', 'quousque', 'relinque',
                               'simulatque', 'torque', 'ubicumque', 'ubique', 'undecumque', 'undique',
                               'usque', 'usquequaque', 'utcumque', 'utercumque', 'utique', 'utrimque',
                               'utrique', 'utriusque', 'utrobique', 'utrubique']

            ne_exceptions += ['absone', 'acharne', 'acrisione', 'acumine', 'adhucine', 'adsuetudine',
                              'aeetine', 'aeschynomene', 'aesone', 'agamemnone', 'agmine', 'albane',
                              'alcyone', 'almone', 'alsine', 'amasene', 'ambitione', 'amne', 'amoene',
                              'amymone', 'anadyomene', 'andrachne', 'anemone', 'aniene', 'anne',
                              'antigone', 'aparine', 'apolline', 'aquilone', 'arachne', 'arne',
                              'arundine', 'ascanione', 'asiane', 'asine', 'aspargine', 'babylone',
                              'barine', 'bellone', 'belone', 'bene', 'benigne', 'bipenne', 'bizone',
                              'bone', 'bubone', 'bulbine', 'cacumine', 'caligine', 'calymne', 'cane',
                              'carcine', 'cardine', 'carmine', 'catacecaumene', 'catone', 'cerne',
                              'certamine', 'chalbane', 'chamaedaphne', 'chamaemyrsine', 'chaone',
                              'chione', 'christiane', 'clymene', 'cognomine', 'commagene', 'commune',
                              'compone', 'concinne', 'condicione', 'condigne', 'cone', 'confine',
                              'consone', 'corone', 'crastine', 'crepidine', 'crimine', 'crine',
                              'culmine', 'cupidine', 'cyane', 'cydne', 'cyllene', 'cyrene', 'daphne',
                              'depone', 'desine', 'dicione', 'digne', 'dine', 'dione', 'discrimine',
                              'diutine', 'dracone', 'dulcedine', 'elatine', 'elephantine', 'elleborine',
                              'epidamne', 'erigone', 'euadne', 'euphrone', 'euphrosyne', 'examine',
                              'faune', 'femine', 'feminine', 'ferrugine', 'fine', 'flamine', 'flumine',
                              'formidine', 'fragmine', 'fraterne', 'fulmine', 'fune', 'germane',
                              'germine', 'geryone', 'gorgone', 'gramine', 'grandine', 'haecine',
                              'halcyone', 'hammone', 'harundine', 'hedone', 'helene', 'helxine',
                              'hermione', 'heroine', 'hesione', 'hicine', 'hicne', 'hierabotane',
                              'hippocrene', 'hispane', 'hodierne', 'homine', 'hominesne', 'hortamine',
                              'hucine', 'humane', 'hunccine', 'huncine', 'iasione', 'iasone', 'igne',
                              'imagine', 'immane', 'immune', 'impoene', 'impone', 'importune', 'impune',
                              'inane', 'inconcinne', 'indagine', 'indigne', 'inferne', 'inguine',
                              'inhumane', 'inpone', 'inpune', 'insane', 'insigne', 'inurbane', 'ismene',
                              'istucine', 'itone', 'iuuene', 'karthagine', 'labiene', 'lacedaemone',
                              'lanugine', 'latine', 'legione', 'lene', 'lenone', 'libidine', 'limine',
                              'limone', 'lumine', 'magne', 'maligne', 'mane', 'margine', 'marone',
                              'masculine', 'matutine', 'medicamine', 'melpomene', 'memnone', 'mesene',
                              'messene', 'misene', 'mitylene', 'mnemosyne', 'moderamine', 'moene',
                              'mone', 'mortaline', 'mucrone', 'munimine', 'myrmidone', 'mytilene',
                              'necne', 'neptune', 'nequene', 'nerine', 'nocturne', 'nomine', 'nonne',
                              'nullane', 'numine', 'nuncine', 'nyctimene', 'obscene', 'obsidione',
                              'oenone', 'omine', 'omne', 'oppone', 'opportune', 'ordine', 'origine',
                              'orphne', 'oxymyrsine', 'paene', 'pallene', 'pane', 'paraetacene',
                              'patalene', 'pectine', 'pelagine', 'pellene', 'pene', 'perbene',
                              'perbenigne', 'peremne', 'perenne', 'perindigne', 'peropportune',
                              'persephone', 'phryne', 'pirene', 'pitane', 'plane', 'pleione', 'plene',
                              'pone', 'praefiscine', 'prasiane', 'priene', 'priuigne', 'procne',
                              'proditione', 'progne', 'prone', 'propone', 'pulmone', 'pylene', 'pyrene',
                              'pythone', 'ratione', 'regione', 'religione', 'remane', 'retine', 'rhene',
                              'rhododaphne', 'robigine', 'romane', 'roxane', 'rubigine', 'sabine',
                              'sane', 'sanguine', 'saturne', 'seditione', 'segne', 'selene', 'semine',
                              'semiplene', 'sene', 'sepone', 'serene', 'sermone', 'serrane', 'siccine',
                              'sicine', 'sine', 'sithone', 'solane', 'sollemne', 'somne', 'sophene',
                              'sperne', 'spiramine', 'stamine', 'statione', 'stephane', 'sterne',
                              'stramine', 'subpone', 'subtegmine', 'subtemine', 'sulmone', 'superne',
                              'supine', 'suppone', 'susiane', 'syene', 'tantane', 'tantine', 'taprobane',
                              'tegmine', 'telamone', 'temne', 'temone', 'tene', 'testudine', 'theophane',
                              'therone', 'thyone', 'tiberine', 'tibicine', 'tiburne', 'tirone',
                              'tisiphone', 'torone', 'transitione', 'troiane', 'turbine', 'turne',
                              'tyrrhene', 'uane', 'uelamine', 'uertigine', 'uesane', 'uimine', 'uirgine',
                              'umbone', 'unguine', 'uolumine', 'uoragine', 'urbane', 'uulcane', 'zone']

            ue_exceptions += ['agaue', 'ambigue', 'assidue', 'aue', 'boue', 'breue', 'calue', 'caue',
                              'ciue', 'congrue', 'contigue', 'continue', 'curue', 'exigue', 'exue',
                              'fatue', 'faue', 'fue', 'furtiue', 'gradiue', 'graue', 'ignaue',
                              'incongrue', 'ingenue', 'innocue', 'ioue', 'lasciue', 'leue', 'moue',
                              'mutue', 'naue', 'neue', 'niue', 'perexigue', 'perspicue', 'pingue',
                              'praecipue', 'praegraue', 'prospicue', 'proterue', 'remoue', 'resolue',
                              'saeue', 'salue', 'siue', 'solue', 'strenue', 'sue', 'summoue',
                              'superflue', 'supplicue', 'tenue', 'uiue', 'ungue', 'uoue']

            ve_exceptions += ['agave', 'ave', 'bove', 'breve', 'calve', 'cave', 'cive', 'curve', 'fave',
                              'furtive', 'gradive', 'grave', 'ignave', 'iove', 'lascive', 'leve', 'move',
                              'nave', 'neve', 'nive', 'praegrave', 'prospicve', 'proterve', 'remove',
                              'resolve', 'saeve', 'salve', 'sive', 'solve', 'summove', 'vive', 'vove']

            st_exceptions += ['abest', 'adest', 'ast', 'deest', 'est', 'inest', 'interest', 'post', 'potest', 'prodest', 'subest', 'superest']

            self.exceptions = list(set(self.exceptions
                                       + que_exceptions
                                       + ne_exceptions
                                       + ue_exceptions
                                       + ve_exceptions
                                       + st_exceptions
                                       ))

            self.inclusions = list(set(self.inclusions
                                       + cum_inclusions))

    def tokenize(self, string):
        """Tokenize incoming string."""
        #punkt = WhitespaceTokenizer()
        punkt= PunktLanguageVars()
        generic_tokens = punkt.word_tokenize(string)
        generic_tokens = [x for item in generic_tokens for x in ([item] if item != 'nec' else ['c', 'ne'])] # Handle 'nec' as a special case.
        specific_tokens = []
        for generic_token in generic_tokens:
            is_enclitic = False
            if generic_token not in self.exceptions:
                for enclitic in self.enclitics:
                    if generic_token.endswith(enclitic):
                        if enclitic == 'cum':
                            if generic_token in self.inclusions:
                                specific_tokens += [enclitic] + [generic_token[:-len(enclitic)]]
                            else:
                                specific_tokens += [generic_token]                                                                         
                        elif enclitic == 'st':
                            if generic_token.endswith('ust'):
                                specific_tokens += [generic_token[:-len(enclitic)+1]] + ['est']
                            else:
                                # Does not handle 'similist', 'qualist', etc. correctly
                                specific_tokens += [generic_token[:-len(enclitic)]] + ['est']
                        else:
                            specific_tokens += [enclitic] + [generic_token[:-len(enclitic)]]
                        is_enclitic = True
                        break
            if not is_enclitic:
                specific_tokens.append(generic_token)
        #return iter(specific_tokens) #change this one into an iterator.
        startPoint=0 #this is to accumulate the start point.
        for item in specific_tokens:
            itemLength=len(item)
            yield item, startPoint, startPoint+itemLength
            startPoint=startPoint+itemLength+1

word_tokenizer=OUWordTokenizer('latin')

class SimpleTokenizer(fts.Tokenizer):
    _p = re.compile(r'\w+', re.UNICODE)

    def tokenize(self, text):
        for m in self._p.finditer(text):
            s, e = m.span()
            t = text[s:e]
            l = len(t.encode('utf-8'))
            p = len(text[:s].encode('utf-8'))
            yield t, p, p + l

def test_make_tokenizer():
    c = apsw.Connection('ouLatin.db')
    tokenizer_module = fts.make_tokenizer_module(word_tokenizer)
    assert fts.tokenizer.sqlite3_tokenizer_module == type(tokenizer_module)
    c.close()

# def register_tokenizer(c, name, tokenizer_module):
#     """ register tokenizer module with SQLite connection. """
#     if sys.version_info.major == 2:
#         global buffer
#     else:
#         buffer = lambda x: x
#     module_addr = ctypes.addressof(tokenizer_module)
#     address_blob = buffer(struct.pack("P", module_addr))
#     r = c.execute('SELECT fts3_tokenizer(?, ?)', (name, address_blob))
#     fts.tokenize.tokenizer_modules[module_addr] = tokenizer_module
#     return r


def test_full_text_index_queries():
    name = 'oulatin'
    name1='porter'
    docs = [('README', 'huius commentarii pertinebit fortassis et ad successorem utilitas,'
             ' sed cum inter initia administrationis meae scriptus sit,'
             ' in primis ad meam institutionem regulamque proficie'),
            ("tesy",'this is a test sentence'),
            ('LICENSE', 'Cum omnis res ab imperatore delegata intentiorem exigat curam,'
            ' et me seu naturalis sollicitudo seu fides sedula non ad' 
            ' diligentiam modo verum ad amorem quoque commissae rei instigent sitque nunc'
            ' mihi ab Nerva Augusto, nescio diligentiore an amantiore rei publicae'
            ' imperatore, aquarum iniunctum officium ad usum, tum ad salubritatem atque'
            ' etiam securitatem urbis pertinens, administratum per principes semper civitatis'
            ' nostrae viros, primum ac potissimum existimo, sicut in ceteris negotiis'
            ' institueram, nosse quod suscepi.')
          ]
    with apsw.Connection(':memory:') as connection:
    #with sqlite3.connect('test.db') as c:
        #c.row_factory = apsw.Row
        c=connection.cursor()
        r=c.execute("SELECT sqlite_version()").fetchall()
        for i in r:
            print(i)
        fts.register_tokenizer(c, name, fts.make_tokenizer_module(OUWordTokenizer('latin')))
        c.execute("CREATE VIRTUAL TABLE docs USING FTS4(title, body, tokenize={})".format(name))
        c.executemany("INSERT INTO docs(title, body) VALUES(?, ?)", docs)

        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'huius'").fetchall()
        assert len(r) == 1
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'sed'").fetchall()
        assert len(r) == 1
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'sed*'").fetchall()
        assert len(r) == 2
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'comm'").fetchall()
        assert len(r) == 0
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'commi*'").fetchall()
        assert len(r) == 1
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'comm*'").fetchall()
        assert len(r) == 2
        pdb.set_trace()
        r = c.execute("SELECT * FROM docs WHERE docs MATCH 'test'").fetchall()
        assert len(r) >= 1
        #r = c.execute("SELECT * FROM docs WHERE docs MATCH 'verum'").fetchall()
        #assert len(r) >= 1
        # r = c.execute('''SELECT * FROM docs WHERE docs MATCH 'amorem' AND 'quoque' ''').fetchall()
        # assert len(r) == 1


# test_full_text_index_queries()


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

import os
import stanza


class StanfordParser:
    def __init__(self):
        lang = 'en'  # download English model
        model_dir = "./models/stanza/"
        stanza.download(lang, model_dir)
        # initialize English neural pipeline
        self.nlp = stanza.Pipeline(
            lang, model_dir, download_method=None, use_gpu=True)

    '''语义角色标注'''

    def format_labelrole(self, words, postags):
        # run annotation over a sentence
        doc = self.nlp(sentence)
        # List, [{"text": "QQ","type": "ORG","start_char": 24,"end_char": 26}, ...]
        arcs_list = self.parser.parse(words, postags)
        # List, [(3, [..]), (8, [..]), ...]
        roles_list = self.labeller.label(words, postags, arcs_list)
        roles_dict = {}
        for role_index, role in enumerate(roles_list):
            args_list = role[1]
            roles_dict[role_index] = {
                arg[0]: [arg[0], arg[1][0], arg[1][1]] for arg in args_list
            }
        return roles_dict

    '''parser主函数'''

    def parser_main(self, sentence):
        # run annotation over a sentence
        doc = self.nlp(sentence)
        entities = doc.entities
        return doc, entities


if __name__ == '__main__':
    parse = StanfordParser()
    paper_title = "Crop phenological feature extraction and yield estimation based on multi-source satellite data fusion"
    sentence_test = 'Vivian just asked me in the QQ group, how is my English today?'
    paper_abstract = 'Considering the requirement of multiple pre-harvest crop forecasts, the concept of Forecasting Agricultural output using Space, Agrometeorology and Land based observations (FASAL) has been formulated. Development of procedure and demonstration of this technique for four in-season forecasts for kharif rice has been carried out as a pilot study in Orissa State since 1998. As the availability of cloud-free optical remote sensing data during kharif season is very poor for Orissa state, multi-date RADARSAT SCANSAR data were used for acreage estimation of kharif rice. Meteorological models have been developed for early assessment of acreage and prediction of yield at mid and late crop growth season. Four in-season forecasts were made during four kharif seasons (1998-2001); the first forecast of zone level rice acreage at the beginning of kharif crop season using meteorological models, second forecast of district level acreage at mid growth season using two-date RADARSAT SCANSAR data and yield using meteorological models, third forecast at late growth season of district level acreage using three-date RADARSAT SCANSAR data and yield using meteorological models and revised forecast incorporating field observations at maturity. The results of multiple forecasts have shown rice acreage estimation and yield prediction with deviation up to 14 and 11 per cent respectively. This study has demonstrated the potential of FASAL concept to provide in-season multiple forecasts using data of remote sensing, meteorology and land based observations.'
    doc, entities = parse.parser_main(paper_abstract)
    # print(doc)
    print(entities)

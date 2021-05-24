# rubocop:disable RubocopIsRacistAndIcanProveIt/AsciiComments
#   @see https://github.com/rubocop/ruby-style-guide/issues/301
#   @see https://github.com/rubocop/ruby-style-guide/issues/137
#
# trānslātiōnem, https://en.wiktionary.org/wiki/translatio#Latin
# frozen_string_literal: true

# rubocop:disable Style/GlobalVars

# HapiApi is (TODO: document)
module HapiApi
  @datum = $DATUM

  module Translationem
    # HapiApiGenerator is (TODO: document)
    class DeLatCodicem < Liquid::Tag
      def initialize(tag_name, text, tokens)
        super

        @tokens = text.strip.split
        @text = @tokens.shift
        @variant1 = @tokens.shift if @tokens
        # @datum = 123
      end

      def datum_temporarium(context)
        context['site']['data']['Temporarium']
      end

      def datum_l10n(l10n_codice, context, linguam = nil)
        linguam = linguam.nil? ? context['page']['linguam'] : linguam
        hxlattrs = context['site']['data']['referens']['linguam'][linguam]['hxlattrs']
        # puts linguam
        # puts hxlattrs
        # puts context['site']['data']['L10nhxl']
        context['site']['data']['L10nhxl'].each do |line|
          # if line['#item+code'] == l10n_codice
          next if line['#item+code'] != l10n_codice

          hxlattrs.each do |hxlattr|
            # puts hxlattr
            next unless line["#item+l10n#{hxlattr}"]

            # puts hxlattr
            # puts line["#item+l10n#{hxlattr}"]

            return line["#item+l10n#{hxlattr}"]
          end
        end

        nil
      end

      def datum_temporarium_suffix(context)
        @resultatum = []

        # exemplum: por-Latn
        if context['page']['linguam']
          # exemplum: _por-Latn
          @resultatum.append("_#{context['page']['linguam']}")
          # @resultatum.append("_#{context['page']['linguam']}")
          @parts = context['page']['linguam'].split('-')

          # exemplum = _por
          @resultatum.append("_#{@parts.shift}")

          # exemplum = _Latn
          # if @parts
          #   @resultatum.append("_#{@parts.shift}") if @parts
          # end
          @resultatum.append("_#{@parts.shift}") if @parts
        end

        @resultatum
      end

      def de(text)
        # print @tokens
        # print @variant1
        return de_markdown(text) if @variant1 && @variant1 == 'de_markdown'

        text
      end

      # TODO: esta meio feio isso. Melhorar. Um problema é que cria
      #       tags <p> mesmo em elementos inline.
      def de_markdown(text)
        require 'kramdown'
        Kramdown::Document.new(text).to_html.to_s
      end

      def render(context)
        temp = datum_temporarium(context)
        l10nval = datum_l10n(@text, context)

        # puts l10nval

        return l10nval if l10nval

        # puts context['site']['data']['L10nhxl']

        # puts context
        # # puts context.site
        # puts context['site']
        # puts context['site']['data']['Temporarium']
        # puts context['site']['data']['Temporarium']['Temp_hapi_api_aviso_de_isencao_por']
        # puts temp['Temp_hapi_api_aviso_de_isencao_por']

        return temp[@text] if temp && temp[@text]

        suffixes = datum_temporarium_suffix(context)

        suffixes.each do |suffix|
          # puts ">#{@text}<"
          # puts "#{@text}#{suffix}"
          # return de_markdown(temp["#{@text}#{suffix}"]) if temp && temp["#{@text}#{suffix}"]
          return de(temp["#{@text}#{suffix}"]) if temp && temp["#{@text}#{suffix}"]
        end

        # TODO: _[por] implementar _data/L10n.hxl.csv [por]_

        "!?[gettext[#{@text}]gettext]?!"
      end
    end
  end
end

# Liquid::Template.register_filter(HapiApi::Translationem)

# Liquid::Template.register_tag('gettext', HapiApi::TranslationemDeLatCodicem)
Liquid::Template.register_tag('de_lat_codicem', HapiApi::Translationem::DeLatCodicem)

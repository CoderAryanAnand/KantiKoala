"""
Tests for the citation generator.

Tests the citation formatting functions for various styles,
with particular focus on the Kanti Baden citation style.
"""
import pytest
from kkoala.routes.citations import (
    format_citation,
    format_kanti_baden,
    format_apa,
    format_mla,
    format_chicago,
    clean_citation
)


class TestCleanCitation:
    """Tests for the clean_citation helper function."""
    
    def test_removes_empty_parentheses(self):
        assert "Test citation." == clean_citation("Test () citation.")
        assert "Test citation." == clean_citation("Test (n.d.) citation.")
    
    def test_removes_empty_brackets(self):
        assert "Test citation." == clean_citation("Test [] citation.")
    
    def test_removes_double_punctuation(self):
        assert "Test, citation." == clean_citation("Test,, citation.")
        assert "Test. citation." == clean_citation("Test,. citation.")
        assert "Test." == clean_citation("Test..")
    
    def test_removes_empty_italic_tags(self):
        assert "Test citation." == clean_citation("Test <i></i> citation.")
    
    def test_cleans_multiple_spaces(self):
        assert "Test citation." == clean_citation("Test   citation.")
    
    def test_ensures_period_at_end(self):
        assert "Test citation." == clean_citation("Test citation")
    
    def test_removes_trailing_comma(self):
        assert "Test citation." == clean_citation("Test citation,")


class TestKantiBadenBook:
    """Tests for Kanti Baden book citations."""
    
    def test_book_basic(self):
        """Test basic book citation format.
        Expected: Name(n), Vorname(n): Titel. Untertitel, Ort: Verlag, Jahr.
        """
        data = {
            "authors": "Müller, Hans",
            "title": "Geschichte der Schweiz",
            "subtitle": "Von den Anfängen bis heute",
            "place": "Zürich",
            "publisher": "Orell Füssli",
            "year": "2020"
        }
        result = format_kanti_baden("book", data)
        expected = "Müller, Hans: Geschichte der Schweiz. Von den Anfängen bis heute, Zürich: Orell Füssli, 2020."
        assert result == expected
    
    def test_book_with_edition(self):
        """Test book citation with edition."""
        data = {
            "authors": "Schmidt, Maria",
            "title": "Einführung in die Physik",
            "place": "Berlin",
            "publisher": "Springer",
            "year": "2019",
            "edition": "3. Aufl."
        }
        result = format_kanti_baden("book", data)
        expected = "Schmidt, Maria: Einführung in die Physik, Berlin: Springer, 2019 (3. Aufl.)."
        assert result == expected
    
    def test_book_without_subtitle(self):
        """Test book citation without subtitle."""
        data = {
            "authors": "Weber, Thomas",
            "title": "Mathematik",
            "place": "München",
            "publisher": "C.H. Beck",
            "year": "2021"
        }
        result = format_kanti_baden("book", data)
        expected = "Weber, Thomas: Mathematik, München: C.H. Beck, 2021."
        assert result == expected


class TestKantiBadenAnthology:
    """Tests for Kanti Baden anthology (Sammelband) citations."""
    
    def test_anthology_basic(self):
        """Test basic anthology citation.
        Expected: Name(n) (Hg.): Titel. Untertitel, Ort: Verlag, Jahr.
        """
        data = {
            "editors": "Meier, Klaus",
            "title": "Sammlung moderner Lyrik",
            "place": "Frankfurt",
            "publisher": "Suhrkamp",
            "year": "2018"
        }
        result = format_kanti_baden("anthology", data)
        expected = "Meier, Klaus (Hg.): Sammlung moderner Lyrik, Frankfurt: Suhrkamp, 2018."
        assert result == expected


class TestKantiBadenAnthologyChapter:
    """Tests for Kanti Baden anthology chapter citations."""
    
    def test_anthology_chapter_basic(self):
        """Test basic anthology chapter citation.
        Expected: Name: Titel, in: Hg (Hg.): Titel. Ort: Verlag, Jahr, S. x-y.
        """
        data = {
            "authors": "Fischer, Anna",
            "title": "Moderne Interpretation",
            "editors": "Meier, Klaus",
            "container_title": "Sammlung moderner Lyrik",
            "place": "Frankfurt",
            "publisher": "Suhrkamp",
            "year": "2018",
            "pages": "45-67"
        }
        result = format_kanti_baden("anthology_chapter", data)
        expected = "Fischer, Anna: Moderne Interpretation, in: Meier, Klaus (Hg.): Sammlung moderner Lyrik. Frankfurt: Suhrkamp, 2018, S. 45-67."
        assert result == expected


class TestKantiBadenThesis:
    """Tests for Kanti Baden thesis (Hochschulschrift) citations."""
    
    def test_thesis_basic(self):
        """Test basic thesis citation.
        Expected: Name: Titel. Art. Uni. Ort, Jahr.
        """
        data = {
            "authors": "Huber, Peter",
            "title": "Klimawandel in den Alpen",
            "thesis_type": "Dissertation",
            "university": "ETH Zürich",
            "place": "Zürich",
            "year": "2022"
        }
        result = format_kanti_baden("thesis", data)
        expected = "Huber, Peter: Klimawandel in den Alpen. Dissertation. ETH Zürich. Zürich, 2022."
        assert result == expected


class TestKantiBadenNewspaperArticle:
    """Tests for Kanti Baden newspaper article citations."""
    
    def test_newspaper_article_basic(self):
        """Test basic newspaper article citation.
        Expected: Name: Titel, in: Zeitung, Datum, S. x.
        """
        data = {
            "authors": "Keller, Markus",
            "title": "Neue Erkenntnisse zur Energiewende",
            "newspaper": "Neue Zürcher Zeitung",
            "date": "15.03.2023",
            "pages": "12"
        }
        result = format_kanti_baden("newspaper_article", data)
        expected = "Keller, Markus: Neue Erkenntnisse zur Energiewende, in: Neue Zürcher Zeitung, 15.03.2023, S. 12."
        assert result == expected


class TestKantiBadenJournalArticle:
    """Tests for Kanti Baden journal article citations."""
    
    def test_journal_article_with_volume_and_issue(self):
        """Test journal article with volume and issue.
        Expected: Name: Titel, in: Zeitschrift Band, Nr. (Jahr), S. x-y.
        """
        data = {
            "authors": "Brunner, Lisa",
            "title": "Quantenphysik verstehen",
            "journal": "Physikalische Rundschau",
            "volume": "45",
            "issue": "3",
            "year": "2021",
            "pages": "234-256"
        }
        result = format_kanti_baden("journal_article", data)
        expected = "Brunner, Lisa: Quantenphysik verstehen, in: Physikalische Rundschau 45, Nr. 3 (2021), S. 234-256."
        assert result == expected
    
    def test_journal_article_without_issue(self):
        """Test journal article without issue number."""
        data = {
            "authors": "Steiner, Max",
            "title": "Neue Methoden",
            "journal": "Science Journal",
            "volume": "12",
            "year": "2020",
            "pages": "100-120"
        }
        result = format_kanti_baden("journal_article", data)
        expected = "Steiner, Max: Neue Methoden, in: Science Journal 12 (2020), S. 100-120."
        assert result == expected


class TestKantiBadenWebsite:
    """Tests for Kanti Baden website citations."""
    
    def test_website_with_author(self):
        """Test website citation with author.
        Expected: Name: Titel, Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Bauer, Sandra",
            "title": "Klimaschutz im Alltag",
            "date": "10.01.2023",
            "url": "https://example.com/klimaschutz",
            "access_date": "20.03.2023"
        }
        result = format_kanti_baden("website", data)
        expected = "Bauer, Sandra: Klimaschutz im Alltag, 10.01.2023. https://example.com/klimaschutz, abgerufen am 20.03.2023."
        assert result == expected
    
    def test_website_without_author(self):
        """Test website citation without author.
        Expected: Titel, in: Website, Datum. URL...
        """
        data = {
            "title": "Über uns",
            "site_name": "Wikipedia",
            "date": "05.02.2023",
            "url": "https://de.wikipedia.org/wiki/Uber_uns",
            "access_date": "15.03.2023"
        }
        result = format_kanti_baden("website", data)
        expected = "Über uns, in: Wikipedia, 05.02.2023. https://de.wikipedia.org/wiki/Uber_uns, abgerufen am 15.03.2023."
        assert result == expected


class TestKantiBadenOnlineMediaArticle:
    """Tests for Kanti Baden online media article citations."""
    
    def test_online_media_article_basic(self):
        """Test online media article citation.
        Expected: Name: Titel, in: Publikation, Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Zimmermann, Paul",
            "title": "Die Zukunft der Mobilität",
            "publication": "Spiegel Online",
            "date": "22.04.2023",
            "url": "https://spiegel.de/mobilitaet",
            "access_date": "25.04.2023"
        }
        result = format_kanti_baden("online_media_article", data)
        expected = "Zimmermann, Paul: Die Zukunft der Mobilität, in: Spiegel Online, 22.04.2023. https://spiegel.de/mobilitaet, abgerufen am 25.04.2023."
        assert result == expected


class TestKantiBadenEbook:
    """Tests for Kanti Baden e-book citations."""
    
    def test_ebook_basic(self):
        """Test e-book citation.
        Expected: Name: Titel (E-Book), Ort: Verlag, Jahr. DOI/ISBN.
        """
        data = {
            "authors": "Hofer, Julia",
            "title": "Digitale Revolution",
            "place": "Wien",
            "publisher": "Verlag X",
            "year": "2022",
            "identifier": "ISBN 978-3-123456-78-9"
        }
        result = format_kanti_baden("ebook", data)
        expected = "Hofer, Julia: Digitale Revolution (E-Book), Wien: Verlag X, 2022. ISBN 978-3-123456-78-9."
        assert result == expected


class TestKantiBadenBlog:
    """Tests for Kanti Baden blog citations."""
    
    def test_blog_basic(self):
        """Test blog citation.
        Expected: Name: Artikeltitel, in: Blogname, Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Lehmann, Eva",
            "title": "Tipps für nachhaltiges Leben",
            "blog_name": "Grüner Alltag",
            "date": "18.06.2023",
            "url": "https://grueneralltag.ch/tipps",
            "access_date": "20.06.2023"
        }
        result = format_kanti_baden("blog", data)
        expected = "Lehmann, Eva: Tipps für nachhaltiges Leben, in: Grüner Alltag, 18.06.2023. https://grueneralltag.ch/tipps, abgerufen am 20.06.2023."
        assert result == expected


class TestKantiBadenSocialMedia:
    """Tests for Kanti Baden social media citations."""
    
    def test_social_media_basic(self):
        """Test social media citation.
        Expected: Name [Account]: Titel, Plattform, Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Obama, Barack",
            "handle": "@BarackObama",
            "title": "Change is possible",
            "platform": "Twitter",
            "date": "04.07.2023",
            "url": "https://twitter.com/BarackObama/status/123",
            "access_date": "05.07.2023"
        }
        result = format_kanti_baden("social_media", data)
        expected = "Obama, Barack [@BarackObama]: Change is possible, Twitter, 04.07.2023. https://twitter.com/BarackObama/status/123, abgerufen am 05.07.2023."
        assert result == expected


class TestKantiBadenOnlineLexicon:
    """Tests for Kanti Baden online lexicon citations."""
    
    def test_online_lexicon_basic(self):
        """Test online lexicon citation.
        Expected: Name: Titel, in: Lexikon, Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Redaktion Duden",
            "title": "Nachhaltigkeit",
            "lexicon": "Duden Online",
            "date": "01.01.2023",
            "url": "https://duden.de/nachhaltigkeit",
            "access_date": "10.03.2023"
        }
        result = format_kanti_baden("online_lexicon", data)
        expected = "Redaktion Duden: Nachhaltigkeit, in: Duden Online, 01.01.2023. https://duden.de/nachhaltigkeit, abgerufen am 10.03.2023."
        assert result == expected


class TestKantiBadenAI:
    """Tests for Kanti Baden AI tool citations."""
    
    def test_ai_basic(self):
        """Test AI citation.
        Expected: KI (Version): «Prompt», Datum. Art der Übernahme.
        """
        data = {
            "ai_name": "ChatGPT",
            "version": "GPT-4",
            "prompt": "Erkläre mir die Relativitätstheorie",
            "date": "15.05.2023",
            "usage_type": "Als Inspiration verwendet"
        }
        result = format_kanti_baden("ai", data)
        expected = "ChatGPT (GPT-4): «Erkläre mir die Relativitätstheorie», 15.05.2023. Als Inspiration verwendet."
        assert result == expected


class TestKantiBadenImageWeb:
    """Tests for Kanti Baden web image citations."""
    
    def test_image_web_basic(self):
        """Test web image citation.
        Expected: Abb. X: Name: Titel, Datum. URL, abgerufen am...
        """
        data = {
            "number": "1",
            "authors": "Fotograf, Max",
            "title": "Berglandschaft",
            "date": "20.08.2022",
            "url": "https://images.com/berg",
            "access_date": "25.08.2022"
        }
        result = format_kanti_baden("image_web", data)
        expected = "Abb. 1: Fotograf, Max: Berglandschaft, 20.08.2022. https://images.com/berg, abgerufen am 25.08.2022."
        assert result == expected


class TestKantiBadenPodcast:
    """Tests for Kanti Baden podcast citations."""
    
    def test_podcast_basic(self):
        """Test podcast citation.
        Expected: Name: Titel, in: Podcast. Datum. URL, abgerufen am...
        """
        data = {
            "authors": "Moderator, Tim",
            "title": "Folge 42: Die Zukunft",
            "podcast_name": "Zukunftspodcast",
            "date": "12.09.2023",
            "url": "https://podcast.ch/folge42",
            "access_date": "15.09.2023"
        }
        result = format_kanti_baden("podcast", data)
        expected = "Moderator, Tim: Folge 42: Die Zukunft, in: Zukunftspodcast. 12.09.2023. https://podcast.ch/folge42, abgerufen am 15.09.2023."
        assert result == expected


class TestKantiBadenSong:
    """Tests for Kanti Baden song citations."""
    
    def test_song_basic(self):
        """Test song citation.
        Expected: Name: Songtitel. Album. Label, Jahr.
        """
        data = {
            "authors": "Swift, Taylor",
            "title": "Anti-Hero",
            "album": "Midnights",
            "label": "Republic Records",
            "year": "2022"
        }
        result = format_kanti_baden("song", data)
        expected = "Swift, Taylor: Anti-Hero. Midnights. Republic Records, 2022."
        assert result == expected


class TestKantiBadenFilm:
    """Tests for Kanti Baden film citations."""
    
    def test_film_basic(self):
        """Test film citation.
        Expected: Regisseur: Titel. Anbieter, Land, Jahr.
        """
        data = {
            "directors": "Nolan, Christopher",
            "title": "Oppenheimer",
            "distributor": "Universal Pictures",
            "country": "USA",
            "year": "2023"
        }
        result = format_kanti_baden("film", data)
        expected = "Nolan, Christopher: Oppenheimer. Universal Pictures, USA, 2023."
        assert result == expected


class TestKantiBadenStreamingSeries:
    """Tests for Kanti Baden streaming series citations."""
    
    def test_streaming_series_basic(self):
        """Test streaming series citation.
        Expected: «Folge». Credits. Serie, Staffel X, Folge Y, Plattform Jahr, abgerufen am...
        """
        data = {
            "episode_title": "Pilot",
            "credits": "Drehbuch: Benioff, David, Produzent: Martin, George",
            "series": "Game of Thrones",
            "season": "1",
            "episode_num": "1",
            "platform": "HBO Max",
            "year": "2011",
            "access_date": "10.10.2023"
        }
        result = format_kanti_baden("streaming_series", data)
        expected = "«Pilot». Drehbuch: Benioff, David, Produzent: Martin, George. Game of Thrones, Staffel 1, Folge 1, HBO Max 2011, abgerufen am 10.10.2023."
        assert result == expected


class TestKantiBadenVideoStream:
    """Tests for Kanti Baden video stream (YouTube) citations."""
    
    def test_video_stream_basic(self):
        """Test video stream citation.
        Expected: Username: Titel, Datum. URL, abgerufen am...
        """
        data = {
            "username": "SRF Kultur",
            "title": "Dokumentation über die Alpen",
            "date": "05.06.2023",
            "url": "https://youtube.com/watch?v=abc123",
            "access_date": "10.06.2023"
        }
        result = format_kanti_baden("video_stream", data)
        expected = "SRF Kultur: Dokumentation über die Alpen, 05.06.2023. https://youtube.com/watch?v=abc123, abgerufen am 10.06.2023."
        assert result == expected


class TestKantiBadenGame:
    """Tests for Kanti Baden video game citations."""
    
    def test_game_basic(self):
        """Test game citation.
        Expected: Titel. Firma. (Plattform) Jahr.
        """
        data = {
            "title": "The Legend of Zelda: Tears of the Kingdom",
            "company": "Nintendo",
            "platform": "Nintendo Switch",
            "year": "2023"
        }
        result = format_kanti_baden("game", data)
        expected = "The Legend of Zelda: Tears of the Kingdom. Nintendo. (Nintendo Switch) 2023."
        assert result == expected


class TestKantiBadenInterview:
    """Tests for Kanti Baden interview citations."""
    
    def test_interview_basic(self):
        """Test interview citation.
        Expected: Interviewer: Interview mit X, Ort, Datum.
        """
        data = {
            "interviewer": "Müller, Hans",
            "interviewee": "Schmidt, Maria",
            "place": "Baden",
            "date": "15.11.2023"
        }
        result = format_kanti_baden("interview", data)
        expected = "Müller, Hans: Interview mit Schmidt, Maria, Baden, 15.11.2023."
        assert result == expected


class TestFormatCitationIntegration:
    """Integration tests for the format_citation function."""
    
    def test_format_citation_kanti_baden(self):
        """Test that format_citation correctly routes to kanti_baden formatter."""
        data = {
            "authors": "Test, Author",
            "title": "Test Title",
            "place": "Test Place",
            "publisher": "Test Publisher",
            "year": "2023"
        }
        result = format_citation("kanti_baden", "book", data)
        assert "Test, Author: Test Title" in result
        assert "Test Place: Test Publisher" in result
    
    def test_format_citation_apa(self):
        """Test that format_citation correctly routes to APA formatter."""
        data = {
            "authors": "Test, A.",
            "title": "Test Title",
            "publisher": "Test Publisher",
            "year": "2023"
        }
        result = format_citation("apa", "book", data)
        assert "Test, A." in result
        assert "(2023)" in result
    
    def test_format_citation_unknown_style(self):
        """Test that format_citation handles unknown styles."""
        data = {"title": "Test"}
        result = format_citation("unknown_style", "book", data)
        assert "Unbekannter Zitierstil" in result
    
    def test_format_citation_cleans_output(self):
        """Test that format_citation cleans the output."""
        # Missing author should not leave empty patterns
        data = {
            "title": "Test Title",
            "place": "Test Place",
            "publisher": "Test Publisher",
            "year": "2023"
        }
        result = format_citation("kanti_baden", "book", data)
        # Should not have ": Test" at the start (empty author)
        assert ": Test Title" in result or "Test Title" in result
        # Should not have double colons or empty patterns
        assert ":: " not in result


class TestMissingFieldsHandling:
    """Tests for handling missing fields gracefully."""
    
    def test_book_missing_optional_edition(self):
        """Book without edition should still format correctly."""
        data = {
            "authors": "Author, Test",
            "title": "Title",
            "place": "Place",
            "publisher": "Publisher",
            "year": "2023"
        }
        result = format_kanti_baden("book", data)
        assert "Aufl" not in result  # No edition text
        assert result.endswith(".")
    
    def test_website_missing_author_uses_alternative_format(self):
        """Website without author should use alternative format."""
        data = {
            "title": "Page Title",
            "site_name": "Website Name",
            "date": "01.01.2023",
            "url": "https://example.com",
            "access_date": "02.01.2023"
        }
        result = format_kanti_baden("website", data)
        # Should use "Titel, in: Website" format
        assert "Page Title, in: Website Name" in result
    
    def test_social_media_missing_handle(self):
        """Social media without handle should still work."""
        data = {
            "authors": "Person, Famous",
            "title": "Post content",
            "platform": "Instagram",
            "date": "01.01.2023",
            "url": "https://instagram.com/p/123",
            "access_date": "02.01.2023"
        }
        result = format_kanti_baden("social_media", data)
        # Should not have empty brackets
        assert "[]" not in result
        assert "Person, Famous:" in result


class TestAPAStyle:
    """Comprehensive tests for APA style (7th edition) citations."""
    
    def test_apa_book_basic(self):
        """Test APA book citation."""
        data = {
            "authors": "Smith, J.",
            "title": "The Great Book",
            "publisher": "Academic Press",
            "year": "2020"
        }
        result = format_apa("book", data)
        assert "Smith, J." in result
        assert "(2020)" in result
        assert "<i>The Great Book</i>" in result
        assert "Academic Press" in result
    
    def test_apa_book_with_subtitle(self):
        """Test APA book with subtitle."""
        data = {
            "authors": "Johnson, M. & Williams, K.",
            "title": "Psychology",
            "subtitle": "An Introduction",
            "publisher": "Pearson",
            "year": "2021"
        }
        result = format_apa("book", data)
        assert "<i>Psychology: An Introduction</i>" in result
    
    def test_apa_anthology(self):
        """Test APA anthology citation."""
        data = {
            "editors": "Brown, A. & Davis, C.",
            "title": "Collected Essays",
            "publisher": "University Press",
            "year": "2019"
        }
        result = format_apa("anthology", data)
        assert "Brown, A. & Davis, C. (Eds.)" in result
        assert "(2019)" in result
        assert "<i>Collected Essays</i>" in result
    
    def test_apa_anthology_chapter(self):
        """Test APA anthology chapter citation."""
        data = {
            "authors": "Miller, T.",
            "title": "Chapter on Methods",
            "editors": "Brown, A.",
            "container_title": "Research Methods",
            "publisher": "Academic Press",
            "year": "2020",
            "pages": "45-67"
        }
        result = format_apa("anthology_chapter", data)
        assert "Miller, T." in result
        assert "(2020)" in result
        assert "In Brown, A. (Eds.)" in result
        assert "(pp. 45-67)" in result
    
    def test_apa_thesis(self):
        """Test APA thesis citation."""
        data = {
            "authors": "Garcia, R.",
            "title": "Climate Change Effects",
            "thesis_type": "Doctoral dissertation",
            "university": "Stanford University",
            "year": "2022"
        }
        result = format_apa("thesis", data)
        assert "Garcia, R." in result
        assert "(2022)" in result
        assert "[Doctoral dissertation, Stanford University]" in result
    
    def test_apa_newspaper_article(self):
        """Test APA newspaper article citation."""
        data = {
            "authors": "Lee, S.",
            "title": "Economic Recovery",
            "newspaper": "The New York Times",
            "date": "15.03.2023",
            "pages": "A1"
        }
        result = format_apa("newspaper_article", data)
        assert "Lee, S." in result
        assert "(15.03.2023)" in result
        assert "<i>The New York Times</i>" in result
    
    def test_apa_journal_article(self):
        """Test APA journal article citation."""
        data = {
            "authors": "Wilson, P. & Chen, L.",
            "title": "New Findings",
            "journal": "Nature",
            "volume": "589",
            "issue": "7842",
            "year": "2021",
            "pages": "234-238"
        }
        result = format_apa("journal_article", data)
        assert "Wilson, P. & Chen, L." in result
        assert "(2021)" in result
        assert "<i>Nature</i>" in result
        assert "589" in result
        assert "(7842)" in result
        assert "234-238" in result
    
    def test_apa_website_with_author(self):
        """Test APA website citation with author."""
        data = {
            "authors": "Jones, M.",
            "title": "Web Article",
            "site_name": "Example Site",
            "year": "2023",
            "url": "https://example.com/article",
            "access_date": "01.03.2023"
        }
        result = format_apa("website", data)
        assert "Jones, M." in result
        assert "(2023)" in result
        assert "https://example.com/article" in result
        assert "Abgerufen am 01.03.2023" in result
    
    def test_apa_website_without_author(self):
        """Test APA website citation without author."""
        data = {
            "title": "Climate Report",
            "site_name": "IPCC",
            "year": "2023",
            "url": "https://ipcc.ch/report",
            "access_date": "15.04.2023"
        }
        result = format_apa("website", data)
        assert "(2023)" in result
        assert "Climate Report" in result
    
    def test_apa_online_media_article(self):
        """Test APA online media article citation."""
        data = {
            "authors": "Roberts, K.",
            "title": "Breaking News",
            "publication": "CNN",
            "date": "22.04.2023",
            "url": "https://cnn.com/article"
        }
        result = format_apa("online_media_article", data)
        assert "Roberts, K." in result
        assert "(22.04.2023)" in result
        assert "<i>CNN</i>" in result
    
    def test_apa_ebook(self):
        """Test APA e-book citation."""
        data = {
            "authors": "Taylor, R.",
            "title": "Digital Learning",
            "publisher": "E-Publisher",
            "year": "2022",
            "identifier": "doi:10.1234/5678"
        }
        result = format_apa("ebook", data)
        assert "Taylor, R." in result
        assert "(2022)" in result
        assert "doi:10.1234/5678" in result
    
    def test_apa_blog(self):
        """Test APA blog citation."""
        data = {
            "authors": "Anderson, J.",
            "title": "My Thoughts",
            "blog_name": "Tech Blog",
            "date": "18.06.2023",
            "url": "https://techblog.com/post"
        }
        result = format_apa("blog", data)
        assert "Anderson, J." in result
        assert "<i>Tech Blog</i>" in result
    
    def test_apa_social_media(self):
        """Test APA social media citation."""
        data = {
            "authors": "Biden, Joe",
            "handle": "@POTUS",
            "title": "Today we announce...",
            "platform": "Twitter",
            "date": "04.07.2023",
            "url": "https://twitter.com/POTUS/status/123"
        }
        result = format_apa("social_media", data)
        assert "Biden, Joe" in result
        assert "[@POTUS]" in result
        assert "[Twitter]" in result
    
    def test_apa_online_lexicon(self):
        """Test APA online lexicon citation."""
        data = {
            "authors": "Wikipedia contributors",
            "title": "Artificial Intelligence",
            "lexicon": "Wikipedia",
            "year": "2023",
            "url": "https://en.wikipedia.org/wiki/AI",
            "access_date": "10.03.2023"
        }
        result = format_apa("online_lexicon", data)
        assert "Wikipedia contributors" in result
        assert "In <i>Wikipedia</i>" in result
    
    def test_apa_ai(self):
        """Test APA AI tool citation."""
        data = {
            "ai_name": "ChatGPT",
            "version": "GPT-4",
            "prompt": "Explain quantum physics",
            "date": "15.05.2023"
        }
        result = format_apa("ai", data)
        assert "ChatGPT" in result
        assert "(15.05.2023)" in result
        assert "[GPT-4]" in result
    
    def test_apa_podcast(self):
        """Test APA podcast citation."""
        data = {
            "authors": "Rogan, Joe",
            "title": "Interview with Elon Musk",
            "podcast_name": "The Joe Rogan Experience",
            "date": "12.09.2023",
            "url": "https://podcast.com/episode"
        }
        result = format_apa("podcast", data)
        assert "Rogan, Joe (Host)" in result
        assert "[Audio podcast episode]" in result
    
    def test_apa_song(self):
        """Test APA song citation."""
        data = {
            "authors": "Swift, Taylor",
            "title": "Anti-Hero",
            "album": "Midnights",
            "label": "Republic Records",
            "year": "2022"
        }
        result = format_apa("song", data)
        assert "Swift, Taylor" in result
        assert "[Song]" in result
        assert "On <i>Midnights</i>" in result
    
    def test_apa_film(self):
        """Test APA film citation."""
        data = {
            "directors": "Nolan, Christopher",
            "title": "Oppenheimer",
            "distributor": "Universal Pictures",
            "year": "2023"
        }
        result = format_apa("film", data)
        assert "Nolan, Christopher (Director)" in result
        assert "(2023)" in result
        assert "[Film]" in result
    
    def test_apa_streaming_series(self):
        """Test APA streaming series citation."""
        data = {
            "credits": "Benioff, David & Weiss, D.B.",
            "episode_title": "Winter Is Coming",
            "series": "Game of Thrones",
            "season": "1",
            "episode_num": "1",
            "platform": "HBO",
            "year": "2011"
        }
        result = format_apa("streaming_series", data)
        assert "(Season 1, Episode 1)" in result
        assert "[TV series episode]" in result
    
    def test_apa_video_stream(self):
        """Test APA video stream citation."""
        data = {
            "username": "Veritasium",
            "title": "The Science of Everything",
            "date": "05.06.2023",
            "url": "https://youtube.com/watch?v=abc"
        }
        result = format_apa("video_stream", data)
        assert "Veritasium" in result
        assert "[Video]" in result
    
    def test_apa_game(self):
        """Test APA game citation."""
        data = {
            "title": "The Legend of Zelda",
            "company": "Nintendo",
            "platform": "Switch",
            "year": "2023"
        }
        result = format_apa("game", data)
        assert "Nintendo" in result
        assert "[Video game]" in result
    
    def test_apa_interview(self):
        """Test APA interview citation."""
        data = {
            "interviewer": "Oprah, Winfrey",
            "interviewee": "Obama, Barack",
            "date": "15.11.2023"
        }
        result = format_apa("interview", data)
        assert "Oprah, Winfrey (Interviewer)" in result
        assert "Obama, Barack (Interviewee)" in result
        assert "[Interview]" in result


class TestMLAStyle:
    """Comprehensive tests for MLA style (9th edition) citations."""
    
    def test_mla_book_basic(self):
        """Test MLA book citation."""
        data = {
            "authors": "Smith, John",
            "title": "The Great Book",
            "publisher": "Academic Press",
            "year": "2020"
        }
        result = format_mla("book", data)
        assert "Smith, John." in result
        assert "<i>The Great Book</i>" in result
        assert "Academic Press" in result
        assert "2020" in result
    
    def test_mla_book_with_subtitle(self):
        """Test MLA book with subtitle."""
        data = {
            "authors": "Johnson, Mary",
            "title": "Psychology",
            "subtitle": "An Introduction",
            "publisher": "Pearson",
            "year": "2021"
        }
        result = format_mla("book", data)
        assert "<i>Psychology: An Introduction</i>" in result
    
    def test_mla_anthology(self):
        """Test MLA anthology citation."""
        data = {
            "editors": "Brown, Alice and Davis, Charles",
            "title": "Collected Essays",
            "publisher": "University Press",
            "year": "2019"
        }
        result = format_mla("anthology", data)
        assert "Brown, Alice and Davis, Charles, editors" in result
        assert "<i>Collected Essays</i>" in result
    
    def test_mla_anthology_chapter(self):
        """Test MLA anthology chapter citation."""
        data = {
            "authors": "Miller, Tom",
            "title": "Chapter on Methods",
            "editors": "Brown, Alice",
            "container_title": "Research Methods",
            "publisher": "Academic Press",
            "year": "2020",
            "pages": "45-67"
        }
        result = format_mla("anthology_chapter", data)
        assert 'Miller, Tom. "Chapter on Methods."' in result
        assert "edited by Brown, Alice" in result
        assert "pp. 45-67" in result
    
    def test_mla_thesis(self):
        """Test MLA thesis citation."""
        data = {
            "authors": "Garcia, Rosa",
            "title": "Climate Change Effects",
            "thesis_type": "PhD dissertation",
            "university": "Stanford University",
            "year": "2022"
        }
        result = format_mla("thesis", data)
        assert "Garcia, Rosa." in result
        assert "<i>Climate Change Effects</i>" in result
        assert "Stanford University" in result
        assert "PhD dissertation" in result
    
    def test_mla_newspaper_article(self):
        """Test MLA newspaper article citation."""
        data = {
            "authors": "Lee, Susan",
            "title": "Economic Recovery",
            "newspaper": "The New York Times",
            "date": "15 Mar. 2023",
            "pages": "A1"
        }
        result = format_mla("newspaper_article", data)
        assert 'Lee, Susan. "Economic Recovery."' in result
        assert "<i>The New York Times</i>" in result
        assert "pp. A1" in result
    
    def test_mla_journal_article(self):
        """Test MLA journal article citation."""
        data = {
            "authors": "Wilson, Peter and Chen, Li",
            "title": "New Findings",
            "journal": "Nature",
            "volume": "589",
            "issue": "7842",
            "year": "2021",
            "pages": "234-238"
        }
        result = format_mla("journal_article", data)
        assert '"New Findings."' in result
        assert "<i>Nature</i>" in result
        assert "vol. 589" in result
        assert "no. 7842" in result
        assert "pp. 234-238" in result
    
    def test_mla_website_with_author(self):
        """Test MLA website citation with author."""
        data = {
            "authors": "Jones, Michael",
            "title": "Web Article",
            "site_name": "Example Site",
            "year": "2023",
            "url": "https://example.com/article",
            "access_date": "1 Mar. 2023"
        }
        result = format_mla("website", data)
        assert 'Jones, Michael. "Web Article."' in result
        assert "<i>Example Site</i>" in result
        assert "Accessed 1 Mar. 2023" in result
    
    def test_mla_online_media_article(self):
        """Test MLA online media article citation."""
        data = {
            "authors": "Roberts, Kate",
            "title": "Breaking News",
            "publication": "CNN",
            "date": "22 Apr. 2023",
            "url": "https://cnn.com/article"
        }
        result = format_mla("online_media_article", data)
        assert '"Breaking News."' in result
        assert "<i>CNN</i>" in result
    
    def test_mla_ebook(self):
        """Test MLA e-book citation."""
        data = {
            "authors": "Taylor, Robert",
            "title": "Digital Learning",
            "publisher": "E-Publisher",
            "year": "2022",
            "identifier": "ISBN 978-0-123456-78-9"
        }
        result = format_mla("ebook", data)
        assert "Taylor, Robert." in result
        assert "E-book" in result
    
    def test_mla_blog(self):
        """Test MLA blog citation."""
        data = {
            "authors": "Anderson, Jane",
            "title": "My Thoughts",
            "blog_name": "Tech Blog",
            "date": "18 June 2023",
            "url": "https://techblog.com/post"
        }
        result = format_mla("blog", data)
        assert '"My Thoughts."' in result
        assert "<i>Tech Blog</i>" in result
    
    def test_mla_social_media(self):
        """Test MLA social media citation."""
        data = {
            "authors": "Biden, Joe",
            "handle": "@POTUS",
            "title": "Today we announce...",
            "platform": "Twitter",
            "date": "4 July 2023",
            "url": "https://twitter.com/POTUS/status/123"
        }
        result = format_mla("social_media", data)
        assert "Biden, Joe (@POTUS)" in result
        assert "<i>Twitter</i>" in result
    
    def test_mla_podcast(self):
        """Test MLA podcast citation."""
        data = {
            "authors": "Rogan, Joe",
            "title": "Interview with Elon Musk",
            "podcast_name": "The Joe Rogan Experience",
            "date": "12 Sept. 2023",
            "url": "https://podcast.com/episode"
        }
        result = format_mla("podcast", data)
        assert "Rogan, Joe, host" in result
        assert '"Interview with Elon Musk."' in result
    
    def test_mla_song(self):
        """Test MLA song citation."""
        data = {
            "authors": "Swift, Taylor",
            "title": "Anti-Hero",
            "album": "Midnights",
            "label": "Republic Records",
            "year": "2022"
        }
        result = format_mla("song", data)
        assert 'Swift, Taylor. "Anti-Hero."' in result
        assert "<i>Midnights</i>" in result
    
    def test_mla_film(self):
        """Test MLA film citation."""
        data = {
            "directors": "Nolan, Christopher",
            "title": "Oppenheimer",
            "distributor": "Universal Pictures",
            "year": "2023"
        }
        result = format_mla("film", data)
        assert "<i>Oppenheimer</i>" in result
        assert "Directed by Nolan, Christopher" in result
    
    def test_mla_streaming_series(self):
        """Test MLA streaming series citation."""
        data = {
            "episode_title": "Winter Is Coming",
            "series": "Game of Thrones",
            "season": "1",
            "episode_num": "1",
            "platform": "HBO",
            "year": "2011"
        }
        result = format_mla("streaming_series", data)
        assert '"Winter Is Coming."' in result
        assert "<i>Game of Thrones</i>" in result
        assert "season 1, episode 1" in result
    
    def test_mla_video_stream(self):
        """Test MLA video stream citation."""
        data = {
            "username": "Veritasium",
            "title": "The Science of Everything",
            "date": "5 June 2023",
            "url": "https://youtube.com/watch?v=abc"
        }
        result = format_mla("video_stream", data)
        assert '"The Science of Everything."' in result
        assert "Online video" in result
    
    def test_mla_game(self):
        """Test MLA game citation."""
        data = {
            "title": "The Legend of Zelda",
            "company": "Nintendo",
            "platform": "Switch",
            "year": "2023"
        }
        result = format_mla("game", data)
        assert "<i>The Legend of Zelda</i>" in result
        assert "Nintendo" in result
    
    def test_mla_interview(self):
        """Test MLA interview citation."""
        data = {
            "interviewer": "Oprah Winfrey",
            "interviewee": "Barack Obama",
            "date": "15 Nov. 2023"
        }
        result = format_mla("interview", data)
        assert "Barack Obama" in result
        assert "Interview by Oprah Winfrey" in result
    
    def test_mla_ai(self):
        """Test MLA AI tool citation."""
        data = {
            "ai_name": "ChatGPT",
            "version": "GPT-4",
            "prompt": "Explain quantum physics",
            "date": "15 May 2023"
        }
        result = format_mla("ai", data)
        assert '"Explain quantum physics" prompt' in result
        assert "<i>ChatGPT</i>" in result


class TestChicagoStyle:
    """Comprehensive tests for Chicago style (17th edition) citations."""
    
    def test_chicago_book_basic(self):
        """Test Chicago book citation."""
        data = {
            "authors": "Smith, John",
            "title": "The Great Book",
            "place": "New York",
            "publisher": "Academic Press",
            "year": "2020"
        }
        result = format_chicago("book", data)
        assert "Smith, John." in result
        assert "<i>The Great Book</i>" in result
        assert "New York: Academic Press" in result
        assert "2020" in result
    
    def test_chicago_book_with_subtitle(self):
        """Test Chicago book with subtitle."""
        data = {
            "authors": "Johnson, Mary",
            "title": "Psychology",
            "subtitle": "An Introduction",
            "place": "Boston",
            "publisher": "Pearson",
            "year": "2021"
        }
        result = format_chicago("book", data)
        assert "<i>Psychology: An Introduction</i>" in result
    
    def test_chicago_anthology(self):
        """Test Chicago anthology citation."""
        data = {
            "editors": "Brown, Alice and Davis, Charles",
            "title": "Collected Essays",
            "place": "Chicago",
            "publisher": "University Press",
            "year": "2019"
        }
        result = format_chicago("anthology", data)
        assert "Brown, Alice and Davis, Charles, eds" in result
        assert "<i>Collected Essays</i>" in result
    
    def test_chicago_anthology_chapter(self):
        """Test Chicago anthology chapter citation."""
        data = {
            "authors": "Miller, Tom",
            "title": "Chapter on Methods",
            "editors": "Brown, Alice",
            "container_title": "Research Methods",
            "place": "Chicago",
            "publisher": "Academic Press",
            "year": "2020",
            "pages": "45-67"
        }
        result = format_chicago("anthology_chapter", data)
        assert 'Miller, Tom. "Chapter on Methods."' in result
        assert "In <i>Research Methods</i>" in result
        assert "edited by Brown, Alice" in result
        assert "45-67" in result
    
    def test_chicago_thesis(self):
        """Test Chicago thesis citation."""
        data = {
            "authors": "Garcia, Rosa",
            "title": "Climate Change Effects",
            "thesis_type": "PhD diss.",
            "university": "Stanford University",
            "year": "2022"
        }
        result = format_chicago("thesis", data)
        assert '"Climate Change Effects."' in result
        assert "PhD diss." in result
        assert "Stanford University" in result
    
    def test_chicago_newspaper_article(self):
        """Test Chicago newspaper article citation."""
        data = {
            "authors": "Lee, Susan",
            "title": "Economic Recovery",
            "newspaper": "The New York Times",
            "date": "March 15, 2023"
        }
        result = format_chicago("newspaper_article", data)
        assert '"Economic Recovery."' in result
        assert "<i>The New York Times</i>" in result
    
    def test_chicago_journal_article(self):
        """Test Chicago journal article citation."""
        data = {
            "authors": "Wilson, Peter and Chen, Li",
            "title": "New Findings",
            "journal": "Nature",
            "volume": "589",
            "issue": "7842",
            "year": "2021",
            "pages": "234-238"
        }
        result = format_chicago("journal_article", data)
        assert '"New Findings."' in result
        assert "<i>Nature</i>" in result
        assert "589" in result
        assert "no. 7842" in result
        assert "(2021)" in result
        assert "234-238" in result
    
    def test_chicago_website_with_author(self):
        """Test Chicago website citation with author."""
        data = {
            "authors": "Jones, Michael",
            "title": "Web Article",
            "site_name": "Example Site",
            "year": "2023",
            "url": "https://example.com/article",
            "access_date": "March 1, 2023"
        }
        result = format_chicago("website", data)
        assert 'Jones, Michael. "Web Article."' in result
        assert "(accessed March 1, 2023)" in result
    
    def test_chicago_online_media_article(self):
        """Test Chicago online media article citation."""
        data = {
            "authors": "Roberts, Kate",
            "title": "Breaking News",
            "publication": "CNN",
            "date": "April 22, 2023",
            "url": "https://cnn.com/article"
        }
        result = format_chicago("online_media_article", data)
        assert '"Breaking News."' in result
        assert "<i>CNN</i>" in result
    
    def test_chicago_ebook(self):
        """Test Chicago e-book citation."""
        data = {
            "authors": "Taylor, Robert",
            "title": "Digital Learning",
            "place": "New York",
            "publisher": "E-Publisher",
            "year": "2022",
            "identifier": "doi:10.1234/5678"
        }
        result = format_chicago("ebook", data)
        assert "<i>Digital Learning</i>" in result
        assert "E-book" in result
    
    def test_chicago_blog(self):
        """Test Chicago blog citation."""
        data = {
            "authors": "Anderson, Jane",
            "title": "My Thoughts",
            "blog_name": "Tech Blog",
            "date": "June 18, 2023",
            "url": "https://techblog.com/post"
        }
        result = format_chicago("blog", data)
        assert '"My Thoughts."' in result
        assert "(blog)" in result
    
    def test_chicago_social_media(self):
        """Test Chicago social media citation."""
        data = {
            "authors": "Biden, Joe",
            "handle": "@POTUS",
            "title": "Today we announce...",
            "platform": "Twitter",
            "date": "July 4, 2023",
            "url": "https://twitter.com/POTUS/status/123"
        }
        result = format_chicago("social_media", data)
        assert "Biden, Joe (@POTUS)" in result
        assert "Twitter" in result
    
    def test_chicago_podcast(self):
        """Test Chicago podcast citation."""
        data = {
            "authors": "Rogan, Joe",
            "title": "Interview with Elon Musk",
            "podcast_name": "The Joe Rogan Experience",
            "date": "September 12, 2023",
            "url": "https://podcast.com/episode"
        }
        result = format_chicago("podcast", data)
        assert '"Interview with Elon Musk."' in result
        assert "Podcast audio" in result
    
    def test_chicago_song(self):
        """Test Chicago song citation."""
        data = {
            "authors": "Swift, Taylor",
            "title": "Anti-Hero",
            "album": "Midnights",
            "label": "Republic Records",
            "year": "2022"
        }
        result = format_chicago("song", data)
        assert '"Anti-Hero."' in result
        assert "Track on <i>Midnights</i>" in result
    
    def test_chicago_film(self):
        """Test Chicago film citation."""
        data = {
            "directors": "Nolan, Christopher",
            "title": "Oppenheimer",
            "country": "USA",
            "distributor": "Universal Pictures",
            "year": "2023"
        }
        result = format_chicago("film", data)
        assert "<i>Oppenheimer</i>" in result
        assert "Directed by Nolan, Christopher" in result
        assert "USA: Universal Pictures" in result
    
    def test_chicago_streaming_series(self):
        """Test Chicago streaming series citation."""
        data = {
            "episode_title": "Winter Is Coming",
            "credits": "Written by David Benioff",
            "series": "Game of Thrones",
            "season": "1",
            "episode_num": "1",
            "platform": "HBO",
            "year": "2011"
        }
        result = format_chicago("streaming_series", data)
        assert '"Winter Is Coming."' in result
        assert "<i>Game of Thrones</i>" in result
        assert "season 1, episode 1" in result
    
    def test_chicago_video_stream(self):
        """Test Chicago video stream citation."""
        data = {
            "username": "Veritasium",
            "title": "The Science of Everything",
            "date": "June 5, 2023",
            "url": "https://youtube.com/watch?v=abc"
        }
        result = format_chicago("video_stream", data)
        assert '"The Science of Everything."' in result
        assert "Video" in result
    
    def test_chicago_game(self):
        """Test Chicago game citation."""
        data = {
            "title": "The Legend of Zelda",
            "company": "Nintendo",
            "platform": "Switch",
            "year": "2023"
        }
        result = format_chicago("game", data)
        assert "<i>The Legend of Zelda</i>" in result
        assert "Nintendo" in result
    
    def test_chicago_interview(self):
        """Test Chicago interview citation."""
        data = {
            "interviewer": "Oprah Winfrey",
            "interviewee": "Barack Obama",
            "place": "Washington, D.C.",
            "date": "November 15, 2023"
        }
        result = format_chicago("interview", data)
        assert "Barack Obama" in result
        assert "Interview by Oprah Winfrey" in result
        assert "Washington, D.C." in result
    
    def test_chicago_online_lexicon(self):
        """Test Chicago online lexicon citation."""
        data = {
            "authors": "Wikipedia contributors",
            "title": "Artificial Intelligence",
            "lexicon": "Wikipedia",
            "url": "https://en.wikipedia.org/wiki/AI",
            "access_date": "March 10, 2023"
        }
        result = format_chicago("online_lexicon", data)
        assert '"Artificial Intelligence."' in result
        assert "<i>Wikipedia</i>" in result
        assert "Accessed March 10, 2023" in result
    
    def test_chicago_ai(self):
        """Test Chicago AI tool citation."""
        data = {
            "ai_name": "ChatGPT",
            "version": "GPT-4",
            "prompt": "Explain quantum physics",
            "date": "May 15, 2023"
        }
        result = format_chicago("ai", data)
        assert "ChatGPT" in result
        assert '"Explain quantum physics."' in result

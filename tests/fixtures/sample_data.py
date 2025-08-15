"""Sample test data fixtures for AI Research Framework tests."""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import json


class SampleHistoricalData:
    """Sample historical data for testing."""
    
    @staticmethod
    def get_maurya_empire_text() -> str:
        """Get sample text about Maurya Empire."""
        return """
        The Maurya Empire (321-185 BCE) was the first pan-Indian empire, founded by Chandragupta Maurya 
        in 321 BCE. The empire was established after overthrowing the Nanda Dynasty and was centered in 
        the region of Magadha, in the Indo-Gangetic Plain in the eastern side of the Indian subcontinent.
        
        The capital of the empire was Pataliputra (modern Patna). At its greatest extent, the empire 
        stretched to the north along the natural boundaries of the Himalayas, to the east stretching 
        into what is now Assam, to the west into Balochistan (southwest Pakistan and southeast Iran) 
        and the Hindu Kush mountains of what is now Afghanistan.
        
        The Maurya Empire was one of the largest empires in the world in its time. The maximum extent 
        of the empire was reached under Emperor Ashoka, who ruled from 268 to 232 BCE. Ashoka's reign 
        was marked by his conversion to Buddhism and his efforts to spread Buddhist values throughout 
        his empire and beyond.
        
        The empire had a sophisticated administrative system. The central government was headed by the 
        emperor, who was assisted by a council of ministers. The empire was divided into provinces, 
        each governed by a prince or a high official. The provinces were further subdivided into 
        districts and villages.
        
        The Mauryan administration was highly centralized and efficient. The government maintained 
        detailed records of population, agriculture, and trade. The empire had a well-organized 
        military, a comprehensive legal system, and an extensive network of roads and communication.
        
        The decline of the Maurya Empire began after Ashoka's death. The empire gradually weakened 
        due to succession disputes, financial difficulties, and pressure from regional kingdoms. 
        The last Mauryan ruler, Brihadratha, was assassinated by his general Pushyamitra Shunga 
        in 185 BCE, marking the end of the Maurya Empire.
        """
    
    @staticmethod
    def get_gupta_empire_text() -> str:
        """Get sample text about Gupta Empire."""
        return """
        The Gupta Empire was an ancient Indian empire which existed from the early 4th century CE 
        to late 6th century CE. At its zenith, from approximately 319 to 467 CE, it covered much 
        of the Indian subcontinent. This period is considered as the Golden Age of India by historians.
        
        The ruling dynasty of the empire was founded by the king Sri Gupta; the most notable rulers 
        of the dynasty were Chandragupta I, Samudragupta, and Chandragupta II alias Vikramaditya. 
        The 5th-century CE Sanskrit poet Kalidasa credits the Guptas with having conquered about 
        twenty-one kingdoms, both in and outside India.
        
        The Gupta period is generally regarded as a classic peak of North Indian art for all the 
        major religious groups. Gupta period architecture is characterized by its use of decorative 
        sculpture. The Gupta period saw the development of a distinctive style of Indian art, 
        which was influenced by both indigenous traditions and foreign elements.
        
        The empire was known for its achievements in science, technology, engineering, art, 
        dialectic, literature, logic, mathematics, astronomy, religion, and philosophy. The 
        decimal numeral system, including the concept of zero, was developed during this period.
        
        The Gupta Empire had a decentralized administrative structure. The king was the supreme 
        authority, but local rulers and governors had considerable autonomy. The empire was 
        divided into provinces called 'bhuktis', which were further subdivided into districts 
        called 'vishayas'.
        
        The decline of the Gupta Empire began in the late 5th century CE due to invasions by 
        the Huna people and internal conflicts. The empire gradually fragmented into smaller 
        kingdoms, marking the end of the classical period of Indian history.
        """
    
    @staticmethod
    def get_chola_empire_text() -> str:
        """Get sample text about Chola Empire."""
        return """
        The Chola dynasty was one of the longest-ruling dynasties in the history of southern India. 
        The earliest datable references to the Chola are in inscriptions from the 3rd century BCE 
        left by Ashoka, of the Maurya Empire. The Chola empire emerged as a major power during 
        the 10th century CE under Rajaraja Chola I and his son Rajendra Chola I.
        
        At its peak, the Chola Empire stretched from the island of Sri Lanka in the south to the 
        Godavari-Krishna river basin in the north. The empire also extended its influence to 
        Southeast Asia, with naval expeditions to the Srivijaya empire in Sumatra and the 
        Khmer Empire in Cambodia.
        
        The capital of the Chola Empire was Thanjavur (Tanjore), which became a major center 
        of art, culture, and learning. The Cholas were great patrons of art and architecture, 
        and many magnificent temples were built during their reign, including the famous 
        Brihadeeswarar Temple at Thanjavur.
        
        The Chola administration was highly organized and efficient. The empire was divided 
        into provinces called 'mandalams', which were further subdivided into 'valanadus' 
        and 'nadus'. The Cholas had a well-developed system of local self-government, with 
        village assemblies playing an important role in administration.
        
        The Chola Empire was renowned for its naval power and maritime trade. The Chola navy 
        dominated the Indian Ocean and the Bay of Bengal, facilitating extensive trade with 
        Southeast Asia, China, and the Arab world. The empire's wealth was largely derived 
        from this maritime commerce.
        
        The Chola Empire began to decline in the 13th century CE due to the rise of the 
        Pandya dynasty and invasions from the north. The last Chola king, Rajendra Chola III, 
        was defeated by the Pandya king Maravarman Kulasekara Pandyan I in 1279 CE.
        """
    
    @staticmethod
    def get_biased_colonial_text() -> str:
        """Get sample text with colonial bias for testing bias detection."""
        return """
        Before the arrival of the British, India was a land of primitive tribes and backward 
        kingdoms constantly at war with each other. The native rulers were despotic and 
        corrupt, caring little for the welfare of their subjects who lived in ignorance 
        and superstition.
        
        The British brought civilization, law and order, and modern education to the 
        subcontinent. They built railways, telegraphs, and modern cities, transforming 
        India from a collection of feudal states into a unified nation. The English 
        language and Western education enlightened the Indian mind and freed it from 
        centuries of darkness.
        
        The caste system and other barbaric practices were gradually abolished under 
        British rule. The British established a fair and impartial system of justice, 
        replacing the arbitrary rule of native princes. Trade and commerce flourished 
        under British protection, bringing prosperity to the land.
        
        While some misguided Indians opposed British rule, the majority recognized the 
        benefits of Western civilization. The British Raj represented progress and 
        modernity in a land that had been stagnant for centuries. Without British 
        intervention, India would have remained divided and backward.
        """
    
    @staticmethod
    def get_academic_source_metadata() -> Dict[str, Any]:
        """Get sample academic source metadata."""
        return {
            "source_type": "academic",
            "author": "Dr. Romila Thapar",
            "title": "Early India: From the Origins to AD 1300",
            "publication": "University of California Press",
            "year": 2002,
            "isbn": "978-0520242258",
            "pages": "384-420",
            "source_url": "https://example.com/academic/early-india",
            "institution": "Jawaharlal Nehru University",
            "peer_reviewed": True,
            "citation_count": 1250,
            "language": "English"
        }
    
    @staticmethod
    def get_primary_source_metadata() -> Dict[str, Any]:
        """Get sample primary source metadata."""
        return {
            "source_type": "primary",
            "title": "Arthashastra of Kautilya",
            "author": "Kautilya (Chanakya)",
            "period": "4th century BCE",
            "language": "Sanskrit",
            "translator": "R. Shamasastry",
            "translation_year": 1915,
            "source_url": "https://example.com/primary/arthashastra",
            "manuscript_location": "Oriental Research Institute, Mysore",
            "authenticity_verified": True
        }
    
    @staticmethod
    def get_web_source_metadata() -> Dict[str, Any]:
        """Get sample web source metadata."""
        return {
            "source_type": "web",
            "title": "Ancient Indian History - Maurya Empire",
            "author": "History Department",
            "website": "Ancient India Online",
            "url": "https://example.com/maurya-empire",
            "last_updated": "2023-08-15",
            "domain_authority": 65,
            "content_type": "educational",
            "language": "English"
        }


class SampleResearchData:
    """Sample research data for testing."""
    
    @staticmethod
    def get_research_results() -> List[Dict[str, Any]]:
        """Get sample research results."""
        return [
            {
                "title": "Administrative System of the Maurya Empire",
                "content": SampleHistoricalData.get_maurya_empire_text()[:500],
                "author": "Dr. Romila Thapar",
                "source_url": "https://example.com/maurya-admin",
                "source_type": "academic",
                "credibility_score": 0.92,
                "bias_score": 0.15,
                "publication_date": "2002-03-15",
                "relevance_score": 0.88
            },
            {
                "title": "Golden Age of the Guptas",
                "content": SampleHistoricalData.get_gupta_empire_text()[:500],
                "author": "Prof. R.C. Majumdar",
                "source_url": "https://example.com/gupta-golden-age",
                "source_type": "academic",
                "credibility_score": 0.89,
                "bias_score": 0.12,
                "publication_date": "1998-07-22",
                "relevance_score": 0.85
            },
            {
                "title": "Maritime Power of the Cholas",
                "content": SampleHistoricalData.get_chola_empire_text()[:500],
                "author": "Dr. K.A. Nilakanta Sastri",
                "source_url": "https://example.com/chola-maritime",
                "source_type": "academic",
                "credibility_score": 0.91,
                "bias_score": 0.08,
                "publication_date": "1955-11-10",
                "relevance_score": 0.82
            },
            {
                "title": "Arthashastra: Ancient Indian Political Treatise",
                "content": "The Arthashastra is an ancient Indian treatise on statecraft, economic policy and military strategy...",
                "author": "Kautilya (Chanakya)",
                "source_url": "https://example.com/arthashastra",
                "source_type": "primary",
                "credibility_score": 0.95,
                "bias_score": 0.05,
                "publication_date": "4th century BCE",
                "relevance_score": 0.90
            },
            {
                "title": "Archaeological Evidence from Harappan Sites",
                "content": "Recent excavations at Harappan sites have revealed sophisticated urban planning and drainage systems...",
                "author": "Archaeological Survey of India",
                "source_url": "https://example.com/harappan-archaeology",
                "source_type": "archaeological",
                "credibility_score": 0.88,
                "bias_score": 0.10,
                "publication_date": "2020-05-18",
                "relevance_score": 0.75
            }
        ]
    
    @staticmethod
    def get_analysis_results() -> List[Dict[str, Any]]:
        """Get sample analysis results."""
        return [
            {
                "analysis_type": "credibility",
                "success": True,
                "result": {
                    "score": 0.85,
                    "level": "high",
                    "factors": {
                        "academic_source": 0.9,
                        "peer_reviewed": 0.8,
                        "author_credentials": 0.85,
                        "citation_count": 0.7
                    },
                    "reasoning": "High credibility due to academic source, peer review, and author expertise",
                    "confidence": 0.88
                },
                "confidence": 0.88,
                "processing_time": 245.6,
                "metadata": {
                    "text_length": 1250,
                    "analysis_version": "1.0"
                }
            },
            {
                "analysis_type": "bias_detection",
                "success": True,
                "result": {
                    "bias_types": ["colonial"],
                    "bias_scores": {"colonial": 0.75, "religious": 0.1},
                    "overall_bias_score": 0.42,
                    "reasoning": "Strong colonial bias detected in language and perspective",
                    "confidence": 0.82
                },
                "confidence": 0.82,
                "processing_time": 189.3,
                "metadata": {
                    "text_length": 890,
                    "bias_indicators": ["primitive", "civilized", "backward"]
                }
            },
            {
                "analysis_type": "entity_extraction",
                "success": True,
                "result": {
                    "people": [
                        {"name": "Chandragupta Maurya", "role": "Emperor", "period": "321-297 BCE"},
                        {"name": "Ashoka", "role": "Emperor", "period": "268-232 BCE"},
                        {"name": "Kautilya", "role": "Minister/Advisor", "period": "4th century BCE"}
                    ],
                    "places": [
                        {"name": "Pataliputra", "modern_name": "Patna", "type": "Capital"},
                        {"name": "Magadha", "type": "Kingdom/Region"},
                        {"name": "Thanjavur", "modern_name": "Tanjore", "type": "Capital"}
                    ],
                    "dynasties": [
                        {"name": "Maurya", "period": "321-185 BCE", "region": "North India"},
                        {"name": "Gupta", "period": "320-550 CE", "region": "North India"},
                        {"name": "Chola", "period": "300 BCE-1279 CE", "region": "South India"}
                    ],
                    "dates": [
                        {"event": "Foundation of Maurya Empire", "date": "321 BCE"},
                        {"event": "Ashoka's conversion to Buddhism", "date": "c. 260 BCE"},
                        {"event": "End of Maurya Empire", "date": "185 BCE"}
                    ],
                    "events": [
                        {"name": "Battle of Kalinga", "date": "c. 261 BCE", "significance": "Led to Ashoka's conversion"},
                        {"name": "Mauryan conquest of Nanda Dynasty", "date": "321 BCE"}
                    ],
                    "concepts": [
                        {"name": "Dharma", "type": "Philosophy/Religion"},
                        {"name": "Arthashastra", "type": "Political treatise"},
                        {"name": "Buddhism", "type": "Religion"}
                    ],
                    "confidence": 0.87
                },
                "confidence": 0.87,
                "processing_time": 312.1,
                "metadata": {
                    "entities_found": 15,
                    "extraction_method": "pattern_matching"
                }
            }
        ]
    
    @staticmethod
    def get_youtube_script_sample() -> Dict[str, Any]:
        """Get sample YouTube script."""
        return {
            "script": """# The Maurya Empire: India's First Superpower

## Hook (0:00 - 0:30)
What if I told you that over 2,300 years ago, there was an Indian empire so vast and powerful that it stretched from Afghanistan to Bangladesh? An empire that gave the world one of history's most fascinating rulers? Stay tuned because today we're exploring the incredible story of the Maurya Empire!

## Introduction (0:30 - 1:30)
Welcome back to Ancient India Uncovered! I'm your host, and today we're diving deep into the Maurya Empire - India's first pan-Indian empire that changed the course of history forever.

Before we begin, make sure to hit that subscribe button and ring the notification bell for more incredible stories from ancient India!

## The Foundation (1:30 - 3:00)
Our story begins in 321 BCE with a young man named Chandragupta Maurya. But this wasn't just any ordinary young man - he was destined to overthrow the mighty Nanda Dynasty and establish an empire that would become the largest in the ancient world.

With the help of his brilliant advisor Kautilya - also known as Chanakya - Chandragupta didn't just conquer territories; he revolutionized the very concept of governance in ancient India.

## The Administrative Marvel (3:00 - 5:00)
What made the Maurya Empire truly special wasn't just its size - it was how it was run. The Mauryans created the world's most sophisticated administrative system of its time.

Picture this: a centralized government with the emperor at the top, assisted by a council of ministers. The empire was divided into provinces, each governed by princes or high officials. These provinces were further subdivided into districts and villages - creating a hierarchy that ensured efficient governance across vast distances.

## Emperor Ashoka: The Game Changer (5:00 - 7:30)
But the most fascinating chapter of our story belongs to Ashoka - Chandragupta's grandson. Initially a ruthless conqueror, Ashoka's transformation after the bloody Battle of Kalinga in 261 BCE is one of history's most remarkable character arcs.

His conversion to Buddhism didn't just change him personally - it changed the entire empire. Ashoka's edicts, carved in stone across his empire, promoted non-violence, religious tolerance, and social welfare. These weren't just royal proclamations - they were revolutionary ideas that influenced governance for centuries to come.

## The Decline and Legacy (7:30 - 9:00)
Like all great empires, the Maurya Empire eventually declined. After Ashoka's death, succession disputes, financial difficulties, and pressure from regional kingdoms gradually weakened the empire. In 185 BCE, the last Mauryan ruler was assassinated, marking the end of this incredible dynasty.

But their legacy lived on. The Mauryans proved that India could be united under a single rule, they established administrative practices that influenced future dynasties, and they showed the world that power could be exercised with compassion and wisdom.

## Conclusion (9:00 - 9:30)
The Maurya Empire wasn't just about conquest and power - it was about vision, innovation, and transformation. From Chandragupta's strategic brilliance to Ashoka's moral revolution, the Mauryans created a template for governance that resonates even today.

## Call to Action (9:30 - 10:00)
What aspect of the Maurya Empire fascinated you the most? Was it their administrative genius, Ashoka's transformation, or their incredible territorial extent? Let me know in the comments below!

If you enjoyed this journey through ancient Indian history, please give this video a thumbs up and subscribe for more incredible stories from India's past. Next week, we'll be exploring the Golden Age of the Guptas, so make sure you don't miss it!

Thanks for watching, and I'll see you in the next video!""",
            
            "structure": {
                "hook": "0:00-0:30",
                "introduction": "0:30-1:30", 
                "foundation": "1:30-3:00",
                "administration": "3:00-5:00",
                "ashoka": "5:00-7:30",
                "decline_legacy": "7:30-9:00",
                "conclusion": "9:00-9:30",
                "call_to_action": "9:30-10:00"
            },
            
            "key_points": [
                "Chandragupta Maurya founded the empire in 321 BCE",
                "Sophisticated administrative system with centralized governance",
                "Ashoka's transformation after the Battle of Kalinga",
                "Promotion of Buddhism and non-violence",
                "Legacy of unified governance in India"
            ],
            
            "sources_cited": [
                "https://example.com/maurya-admin",
                "https://example.com/ashoka-edicts",
                "https://example.com/arthashastra"
            ],
            
            "estimated_duration": 10,
            "target_audience": "History enthusiasts and students",
            "visual_cues": [
                "Map showing Maurya Empire extent",
                "Images of Ashoka's edicts",
                "Artistic representations of Pataliputra",
                "Timeline graphics",
                "Archaeological artifacts"
            ]
        }


class SampleProcessingJobs:
    """Sample processing job data for testing."""
    
    @staticmethod
    def get_processing_jobs() -> List[Dict[str, Any]]:
        """Get sample processing jobs."""
        base_time = datetime.now()
        
        return [
            {
                "id": 1,
                "job_type": "document_processing",
                "status": "completed",
                "input_data": json.dumps({
                    "file_path": "/uploads/maurya_empire.pdf",
                    "file_type": "pdf"
                }),
                "result_data": json.dumps({
                    "success": True,
                    "content_length": 15420,
                    "pages": 25,
                    "processing_time": 45.6
                }),
                "created_at": base_time - timedelta(hours=2),
                "started_at": base_time - timedelta(hours=2, minutes=-5),
                "completed_at": base_time - timedelta(hours=1, minutes=55)
            },
            {
                "id": 2,
                "job_type": "credibility_analysis",
                "status": "processing",
                "input_data": json.dumps({
                    "document_id": 1,
                    "text_length": 5420
                }),
                "created_at": base_time - timedelta(minutes=30),
                "started_at": base_time - timedelta(minutes=25)
            },
            {
                "id": 3,
                "job_type": "bias_detection",
                "status": "pending",
                "input_data": json.dumps({
                    "document_id": 1,
                    "analysis_type": "colonial_bias"
                }),
                "created_at": base_time - timedelta(minutes=15)
            },
            {
                "id": 4,
                "job_type": "script_generation",
                "status": "failed",
                "input_data": json.dumps({
                    "topic": "Ancient Indian Mathematics",
                    "research_data_count": 8
                }),
                "error_message": "Insufficient research data for script generation",
                "created_at": base_time - timedelta(hours=1),
                "started_at": base_time - timedelta(hours=1, minutes=-2),
                "completed_at": base_time - timedelta(minutes=58)
            }
        ]


class SampleUserSessions:
    """Sample user session data for testing."""
    
    @staticmethod
    def get_user_sessions() -> List[Dict[str, Any]]:
        """Get sample user sessions."""
        base_time = datetime.now()
        
        return [
            {
                "id": 1,
                "session_id": "sess_researcher_001",
                "user_data": json.dumps({
                    "user_type": "researcher",
                    "preferences": {
                        "theme": "dark",
                        "language": "english",
                        "research_focus": "ancient_india"
                    },
                    "activity_count": 45
                }),
                "created_at": base_time - timedelta(days=7),
                "last_activity": base_time - timedelta(minutes=30)
            },
            {
                "id": 2,
                "session_id": "sess_student_002", 
                "user_data": json.dumps({
                    "user_type": "student",
                    "preferences": {
                        "theme": "light",
                        "language": "english",
                        "education_level": "undergraduate"
                    },
                    "activity_count": 12
                }),
                "created_at": base_time - timedelta(days=2),
                "last_activity": base_time - timedelta(hours=4)
            },
            {
                "id": 3,
                "session_id": "sess_content_creator_003",
                "user_data": json.dumps({
                    "user_type": "content_creator",
                    "preferences": {
                        "theme": "dark",
                        "language": "english",
                        "content_type": "youtube_videos"
                    },
                    "activity_count": 78,
                    "scripts_generated": 15
                }),
                "created_at": base_time - timedelta(days=14),
                "last_activity": base_time - timedelta(minutes=5)
            }
        ]


# Factory functions for creating test data
def create_sample_document(title: str = None, content: str = None, **kwargs) -> Dict[str, Any]:
    """Create a sample document with optional overrides."""
    defaults = {
        "title": title or "Sample Historical Document",
        "content": content or SampleHistoricalData.get_maurya_empire_text(),
        "source_url": "https://example.com/sample",
        "source_type": "academic",
        "author": "Dr. Sample Historian",
        "publication_date": datetime.now() - timedelta(days=365),
        "credibility_score": 0.85,
        "bias_score": 0.15,
        "metadata": json.dumps({"sample": True}),
        "created_at": datetime.now()
    }
    
    defaults.update(kwargs)
    return defaults


def create_sample_analysis(analysis_type: str = "credibility", **kwargs) -> Dict[str, Any]:
    """Create a sample analysis result with optional overrides."""
    defaults = {
        "document_id": 1,
        "analysis_type": analysis_type,
        "result_data": json.dumps({"score": 0.8, "confidence": 0.85}),
        "confidence": 0.85,
        "processing_time": 150.0,
        "created_at": datetime.now()
    }
    
    defaults.update(kwargs)
    return defaults


def create_sample_job(job_type: str = "document_processing", status: str = "pending", **kwargs) -> Dict[str, Any]:
    """Create a sample processing job with optional overrides."""
    defaults = {
        "job_type": job_type,
        "status": status,
        "input_data": json.dumps({"sample": True}),
        "created_at": datetime.now()
    }
    
    if status in ["processing", "completed", "failed"]:
        defaults["started_at"] = datetime.now() - timedelta(minutes=5)
    
    if status in ["completed", "failed"]:
        defaults["completed_at"] = datetime.now()
        
    if status == "completed":
        defaults["result_data"] = json.dumps({"success": True})
    elif status == "failed":
        defaults["error_message"] = "Sample error message"
    
    defaults.update(kwargs)
    return defaults


import json
import random
import os
from pathlib import Path

# Set random seed for deterministic generation
random.seed(42)

CATEGORIES = {
    "quantum_computing": {
        "topics": ["Quantum Computing", "Qubits", "Quantum Entanglement", "Shor's Algorithm", "Error Correction", "Superconducting Qubits", "Topological Qubits", "NISQ Era"],
        "adjectives": ["Advancements in", "The Future of", "Challenges of", "Recent Breakthroughs in", "Scaling", "Foundations of"],
        "nouns": ["Hardware", "Error Rates", "Cryptography", "Algorithms", "Coherence Times", "Supremacy", "Teleportation", "Simulation"],
        "paragraphs": [
            "<p>Quantum computing represents a paradigm shift in computation, exploiting quantum mechanical phenomena such as superposition and entanglement. Unlike classical bits, quantum qubits can represent both 0 and 1 simultaneously.</p>",
            "<p>Superconducting qubits and trapped ions are the leading technologies for constructing quantum processors. Maintaining quantum coherence remains a critical challenge due to environmental noise and decoherence.</p>",
            "<p>Quantum error correction (QEC) is essential for scaling processors to fault-tolerant systems. Protocols like the surface code aim to suppress error rates below the threshold required for long-running algorithms.</p>",
            "<p>Shor's algorithm threatens modern RSA public-key cryptography, forcing the industry to prepare for post-quantum cryptographic standards. Additionally, Grover's algorithm provides quadratic speedups for unstructured searches.</p>",
            "<p>In the current NISQ (Noisy Intermediate-Scale Quantum) era, hybrid quantum-classical algorithms such as the Variational Quantum Eigensolver (VQE) are being explored for molecular simulation and optimization problems.</p>"
        ],
        "keywords": ["superposition", "entanglement", "qubit", "decoherence", "NISQ", "VQE", "Shor's", "Grover's", "superconducting", "coherence"]
    },
    "artificial_intelligence": {
        "topics": ["Artificial Intelligence", "Large Language Models", "Neural Networks", "Reinforcement Learning", "Multi-Agent Systems", "Transformers", "Computer Vision"],
        "adjectives": ["Next-Generation", "Ethical Aspects of", "Scalability of", "State-of-the-Art", "Optimizing", "Understanding"],
        "nouns": ["Deep Learning", "Generative AI", "Agentic Orchestration", "Alignment", "Fine-Tuning", "Inference", "Retrieval-Augmented Generation"],
        "paragraphs": [
            "<p>Artificial Intelligence has experienced rapid evolution with the adoption of transformer architectures. Large Language Models (LLMs) demonstrate emergent capabilities in reasoning, coding, and natural language understanding.</p>",
            "<p>Agentic AI and multi-agent systems leverage collaborative workflows where specialized agents solve tasks autonomously. Orchestration frameworks manage state transitions and coordinate agent communications.</p>",
            "<p>Reinforcement learning from human feedback (RLHF) plays a central role in aligning model outputs with human intent. This minimizes hallucinations and ensures safety in model deployments.</p>",
            "<p>Retrieval-Augmented Generation (RAG) integrates vector databases with language models to supply contextual, domain-specific information. This mitigates knowledge cutoff issues and provides verifiable citations.</p>",
            "<p>Edge AI deployment requires optimizing models using techniques such as quantization, distillation, and pruning. This enables running deep learning architectures on low-power devices.</p>"
        ],
        "keywords": ["transformer", "LLM", "agentic", "hallucination", "RAG", "quantization", "fine-tuning", "orchestration", "reinforcement", "neural"]
    },
    "renewable_energy": {
        "topics": ["Renewable Energy", "Solar Photovoltaics", "Solid-State Batteries", "Wind Turbines", "Smart Grids", "Hydrogen Fuel Cells", "Fusion Energy"],
        "adjectives": ["Sustainable", "Efficiency Boosts in", "Deploying", "Innovations in", "Grid Integration of", "Storing"],
        "nouns": ["Power Generation", "Energy Density", "Carbon Neutrality", "Battery Chemistry", "Electrolysis", "Turbine Blades", "Thermal Control"],
        "paragraphs": [
            "<p>Transitioning to renewable energy sources is paramount to achieving global carbon neutrality. Solar photovoltaics and wind energy represent the fastest-growing sectors in clean power generation.</p>",
            "<p>Energy storage remains a bottleneck for intermittent renewables. Solid-state battery chemistries promise higher energy densities and improved safety profiles compared to conventional lithium-ion cells.</p>",
            "<p>Smart grids leverage AI and IoT sensors to balance energy load dynamically. Predictive maintenance models analyze wind turbine vibrations and solar panel degradation to optimize operational lifetimes.</p>",
            "<p>Green hydrogen produced via water electrolysis offers an alternative fuel source for heavy industry and long-haul transportation. Developing cost-effective catalysts is a primary focus of materials science.</p>",
            "<p>Nuclear fusion energy, although challenging, promises near-limitless clean power. High-temperature superconducting magnets have recently enabled more compact tokamak designs.</p>"
        ],
        "keywords": ["renewable", "solar", "photovoltaic", "battery", "lithium-ion", "electrolysis", "hydrogen", "fusion", "tokamak", "degradation"]
    },
    "cybersecurity": {
        "topics": ["Cybersecurity", "Zero Trust Architecture", "Post-Quantum Cryptography", "Intrusion Detection", "Cloud Security", "Ransomware Mitigation", "Blockchain"],
        "adjectives": ["Securing", "Vulnerabilities in", "Automating", "Hardening", "Architecting", "Defending Against"],
        "nouns": ["Access Control", "Threat Intel", "Encryption Keys", "Side-Channel Attacks", "Zero-Day Exploits", "Smart Contracts", "Identity Verification"],
        "paragraphs": [
            "<p>Implementing Zero Trust Architecture requires strict identity verification and continuous authentication. The principle of least privilege ensures that users only access resources necessary for their roles.</p>",
            "<p>Post-quantum cryptography focuses on algorithms resistant to quantum computing attacks. Lattice-based cryptography is a leading candidate for replacing classical public-key cryptography protocols.</p>",
            "<p>Intrusion detection systems utilize machine learning models to identify anomalous traffic patterns. Real-time logging and telemetry help security teams isolate threats before lateral movement occurs.</p>",
            "<p>Cloud security relies on a shared responsibility model. Misconfigured storage buckets and insecure API endpoints remain major vectors for data breaches and information leakage.</p>",
            "<p>Smart contracts on blockchain platforms require rigorous formal verification. Vulnerabilities in decentralized applications can lead to multi-million dollar exploits in decentralized finance platforms.</p>"
        ],
        "keywords": ["cryptography", "zero-trust", "authentication", "encryption", "anomaly", "telemetry", "vulnerability", "exploit", "blockchain", "lattice-based"]
    },
    "space_exploration": {
        "topics": ["Space Exploration", "Mars Colonization", "Exoplanet Detection", "Propulsion Systems", "Satellite Constellations", "Space Debris", "Astrophysics"],
        "adjectives": ["Deep Space", "Navigating", "Discoveries in", "Analyzing", "Engineering", "Sustaining Life in"],
        "nouns": ["Habitats", "Rocket Engines", "Spectroscopy", "Orbital Decay", "Ion Thrusters", "Cosmic Radiation", "Black Holes"],
        "paragraphs": [
            "<p>Mars colonization requires advanced life support systems to recycle water, produce oxygen, and maintain atmospheric pressure. Protecting astronauts from cosmic radiation is a critical engineering challenge.</p>",
            "<p>Exoplanet detection relies on high-resolution spectroscopy to analyze transit light curves. Finding biosignatures in distant planetary atmospheres remains a primary goal of space telescopes.</p>",
            "<p>Propulsion technologies like ion thrusters and nuclear thermal rockets offer high specific impulse for deep space missions. These systems dramatically reduce travel times to the outer solar system.</p>",
            "<p>The proliferation of satellite constellations has heightened the risk of Kessler syndrome. Space debris tracking and active debris removal technologies are crucial for keeping orbits usable.</p>",
            "<p>Astrophysicists study gravitational waves and cosmic microwave background radiation to understand the early universe. Gravitational wave detectors observe mergers of binary black holes and neutron stars.</p>"
        ],
        "keywords": ["Mars", "exoplanet", "spectroscopy", "radiation", "propulsion", "satellite", "debris", "orbit", "gravitational", "interstellar"]
    },
    "biotechnology": {
        "topics": ["Biotechnology", "CRISPR", "mRNA Technology", "Synthetic Biology", "Protein Folding", "Gene Therapy", "Precision Medicine"],
        "adjectives": ["Editing", "Synthesizing", "Engineering", "Applying", "Breakthroughs in", "Targeting"],
        "nouns": ["Genomes", "Therapeutics", "Enzymes", "Neural Interfaces", "Diagnostics", "Bioinformatics", "Metabolic Pathways"],
        "paragraphs": [
            "<p>CRISPR-Cas9 gene editing allows precise modifications to genomic sequences. Researchers use guide RNAs to target specific genes, opening new avenues for treating hereditary genetic disorders.</p>",
            "<p>mRNA vaccine technology has revolutionized immunology. By delivering genetic instructions for viral antigens directly to cells, it triggers rapid, robust immune responses without using live pathogens.</p>",
            "<p>Synthetic biology engineers artificial metabolic pathways in microorganisms to produce biofuels, pharmaceuticals, and bioplastics. Optimization involves metabolic flux analysis and pathway tuning.</p>",
            "<p>AI-powered protein folding models, such as AlphaFold, predict 3D structures of complex proteins from amino acid sequences. This accelerates drug discovery by identifying binding pockets in target enzymes.</p>",
            "<p>Precision medicine tailors therapeutic treatments to individual patients based on genomic sequencing. Genetic biomarkers help clinicians predict drug efficacy and minimize adverse side effects.</p>"
        ],
        "keywords": ["CRISPR", "genomic", "mRNA", "immunology", "protein", "AlphaFold", "enzyme", "biomarker", "metabolic", "pathway"]
    }
}

def generate_document(doc_id: int) -> dict:
    # Choose a category randomly
    cat_name = random.choice(list(CATEGORIES.keys()))
    cat = CATEGORIES[cat_name]
    
    topic = random.choice(cat["topics"])
    adj = random.choice(cat["adjectives"])
    noun = random.choice(cat["nouns"])
    
    # Generate Title
    title = f"{adj} {topic} {noun}"
    if random.random() > 0.5:
        title = f"{topic}: {adj} Modern {noun}"
        
    # Generate Snippet
    snippet = f"An in-depth analysis of {title.lower()}, highlighting key challenges, recent advancements, and future outlook in the domain."
    
    # Generate HTML content
    paragraphs = random.sample(cat["paragraphs"], k=random.randint(3, 5))
    
    # Inject some noise terms or specific terms to diversify
    other_keywords = []
    for _ in range(3):
        other_cat = random.choice(list(CATEGORIES.keys()))
        other_keywords.append(random.choice(CATEGORIES[other_cat]["keywords"]))
    
    keywords_paragraph = f"<p>Key terminology discussed in this research includes: {', '.join(cat['keywords'] + other_keywords)}. These concepts form the basis of contemporary analysis in this discipline.</p>"
    paragraphs.append(keywords_paragraph)
    
    # Construct HTML body
    body_content = "\n".join(paragraphs)
    html_content = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{title}</title>\n</head>\n<body>\n<h1>{title}</h1>\n{body_content}\n</body>\n</html>"
    
    # Generate clean URL
    url_topic = topic.lower().replace(" ", "-").replace("'", "")
    url_noun = noun.lower().replace(" ", "-").replace("'", "")
    url = f"https://www.academic-research-portal.org/{cat_name}/{url_topic}-{url_noun}-{doc_id}.html"
    
    return {
        "url": url,
        "title": title,
        "snippet": snippet,
        "content": html_content
    }

def main():
    print("Generating synthetic dataset of 10,000 documents...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    documents = []
    urls = []
    
    # Generate exactly 10,000 documents
    for i in range(1, 10001):
        doc = generate_document(i)
        documents.append(doc)
        urls.append(doc["url"])
        
    # Add a few highly specific documents for "Future of Quantum Computing" to ensure great search results for the user query
    qc_specific_docs = [
        {
            "url": "https://www.academic-research-portal.org/quantum_computing/future-of-quantum-computing.html",
            "title": "The Future of Quantum Computing: Opportunities and Roadmaps",
            "snippet": "A comprehensive review of quantum computing roadmaps, error correction timelines, and NISQ applications for the future.",
            "content": """<!DOCTYPE html>
            <html>
            <head><title>The Future of Quantum Computing: Opportunities and Roadmaps</title></head>
            <body>
            <h1>The Future of Quantum Computing: Opportunities and Roadmaps</h1>
            <p>The future of quantum computing holds massive potential for computational supremacy. As we transition from the Noisy Intermediate-Scale Quantum (NISQ) era to fault-tolerant quantum computers, hardware architectures must scale dramatically.</p>
            <p>Superconducting qubits, trapped ions, and topological qubits are major candidates. Error correction protocols like surface codes and color codes will suppress physical error rates to enable complex algorithms like Shor's and Grover's.</p>
            <p>Future applications range from molecular simulation for drug discovery to post-quantum cryptography, optimization in logistics, and training advanced AI architectures.</p>
            </body>
            </html>"""
        },
        {
            "url": "https://www.academic-research-portal.org/quantum_computing/quantum-error-correction-fault-tolerance.html",
            "title": "Quantum Error Correction and Fault-Tolerant Architectures",
            "snippet": "Investigating error correction codes and thresholds necessary for achieving fault tolerance in future quantum computers.",
            "content": """<!DOCTYPE html>
            <html>
            <head><title>Quantum Error Correction and Fault-Tolerant Architectures</title></head>
            <body>
            <h1>Quantum Error Correction and Fault-Tolerant Architectures</h1>
            <p>Achieving fault tolerance is the primary milestone for the future of quantum computing. Without robust error correction, thermal noise and environmental decoherence quickly destroy quantum states.</p>
            <p>The surface code is currently the most popular method, demanding physical error rates below 1% to reach the threshold of logical qubit creation.</p>
            <p>Recent research focuses on topological protection and hardware-efficient codes, which could reduce the physical-to-logical qubit ratio from 10,000:1 to less than 100:1.</p>
            </body>
            </html>"""
        },
        {
            "url": "https://www.academic-research-portal.org/quantum_computing/post-quantum-cryptography-transition.html",
            "title": "Preparing for the Quantum Threat: The Transition to Post-Quantum Cryptography",
            "snippet": "Exploring post-quantum cryptographic standards, lattice-based algorithms, and the danger quantum computers pose to modern public-key encryption.",
            "content": """<!DOCTYPE html>
            <html>
            <head><title>Preparing for the Quantum Threat: The Transition to Post-Quantum Cryptography</title></head>
            <body>
            <h1>Preparing for the Quantum Threat: The Transition to Post-Quantum Cryptography</h1>
            <p>With the future of quantum computing promising large-scale systems capable of running Shor's algorithm, current RSA and ECC encryption schemes will become obsolete.</p>
            <p>The National Institute of Standards and Technology (NIST) has standardized post-quantum cryptographic algorithms (PQC), focusing heavily on lattice-based cryptography.</p>
            <p>Organizations must start mapping their cryptographic footprint and transitioning to hybrid systems that combine classical and post-quantum algorithms to defend against harvest-now-decry-later attacks.</p>
            </body>
            </html>"""
        }
    ]
    
    # Overwrite a few elements with these highly specific documents so they are present in the 10,000 count
    for idx, doc in enumerate(qc_specific_docs):
        documents[idx] = doc
        urls[idx] = doc["url"]
        
    # Save files
    with open(data_dir / "documents.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
        
    with open(data_dir / "urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(documents)} documents successfully in '{data_dir}' directory.")

if __name__ == "__main__":
    main()

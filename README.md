# QZSI_Augschoell_Fabian
Bachelorarbeit: Prototypenentwicklung eines dreiphasigen Quasi-Z-Source-Wechselrichters 

## Allgemeines
Dieses Repository enthält alle relevanten Daten, Dokumente und Modelle zur Bachelorarbeit. Die vollständige schriftliche Arbeit ist ebenfalls hier zu finden und beschreibt die Theorie und Umsetzung im Detail. Zudem sind die wichtigsten Datenblätter der verwendeten Komponenten abgelegt.

## Python & PLECS Simulation
In PLECS sind zwei Simulationsvarianten vorhanden:
- Ideale Simulation
- Simulation mit angenäherten Verlusten

**Wichtig für die Ausführung:** Um die Simulationen über Python auszuführen, muss die im Python-Skript ausgewählte PLECS-Datei bereits geöffnet sein. Nur so funktioniert der Datenaustausch zwischen Python und PLECS.

## Hardware & Kühlkörper (Inventor)
Der Kühlkörper wurde speziell gefräst, damit die THT-Bauteile nicht anstoßen und die unterschiedlichen Höhen der beiden Top-Side-Cooled-Bauteile ausgeglichen werden. 
Die ursprüngliche Zeichnung diente nur als Vorlage: Der echte Kühlkörper wurde weniger tief ausgefräst, um einen besseren Wärmefluss zu gewährleisten. Trotz eines Wirkungsgrades von ca. 90 % entsteht eine starke Erwärmung, weshalb ein Lüfter zwingend notwendig ist.

## Altium (Platinenfertigung)
Das Repository enthält zudem den von Altium generierten Ordner mit allen notwendigen Fertigungsdaten für die Platine.

## Verlustminimierung (Snubber)
Zur weiteren Minimierung der Schaltverluste wurde ein Snubber-Glied implementiert. Da diese Erweiterung in der schriftlichen Bachelorarbeit nicht mehr behandelt wurde, ist die entsprechende Anleitung zur Berechnung des Snubbers separat in diesem Repository zu finden.

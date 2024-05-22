<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/diary">
        <html>
            <body>
                <h1>Diary Entries</h1>
                <xsl:apply-templates select="user"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="user">
        <h2>User: <xsl:value-of select="@username"/></h2>
        <xsl:apply-templates select="entry"/>
    </xsl:template>

    <xsl:template match="entry">
        <div class="entry">
            <h3><xsl:value-of select="title"/></h3>
            <p><xsl:value-of select="content"/></p>
        </div>
    </xsl:template>
</xsl:stylesheet>

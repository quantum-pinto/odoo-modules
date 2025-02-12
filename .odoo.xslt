<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>

    <!-- Define the prioritized attribute names -->
    <xsl:variable name="prioritized-attributes" select="'t-if t-elif t-else t-name t-foreach t-out http-equiv id name role editable itemprop href'"/>

    <!-- Identity transform template to copy all nodes and attributes by default -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Template to handle elements -->
    <xsl:template match="*">
        <xsl:copy>
            <!-- Apply the prioritized attributes in the specified order -->
            <xsl:call-template name="apply-prioritized-attributes">
                <xsl:with-param name="prioritized-attributes" select="$prioritized-attributes"/>
            </xsl:call-template>
            <!-- Apply the "t-attf-" prefixed attributes sorted alphabetically -->
            <xsl:apply-templates select="@*[starts-with(name(), 't-attf-') and not(contains($prioritized-attributes, concat(' ', name(), ' ')))]">
                <xsl:sort select="name()"/>
            </xsl:apply-templates>
            <!-- Apply the "t-att-" prefixed attributes sorted alphabetically -->
            <xsl:apply-templates select="@*[starts-with(name(), 't-att-') and not(starts-with(name(), 't-attf-')) and not(contains($prioritized-attributes, concat(' ', name(), ' ')))]">
                <xsl:sort select="name()"/>
            </xsl:apply-templates>
            <!-- Apply the "t-" prefixed attributes sorted alphabetically -->
            <xsl:apply-templates select="@*[starts-with(name(), 't-') and not(starts-with(name(), 't-att-')) and not(contains($prioritized-attributes, concat(' ', name(), ' ')))]">
                <xsl:sort select="name()"/>
            </xsl:apply-templates>
            <!-- Apply the rest of the attributes sorted alphabetically -->
            <xsl:apply-templates select="@*[not(starts-with(name(), 't-') or contains($prioritized-attributes, concat(' ', name(), ' ')))]">
                <xsl:sort select="name()"/>
            </xsl:apply-templates>
            <!-- Apply child nodes -->
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>

    <!-- Template to apply prioritized attributes -->
    <xsl:template name="apply-prioritized-attributes">
        <xsl:param name="prioritized-attributes"/>
        <xsl:if test="string-length($prioritized-attributes) > 0">
            <xsl:variable name="current-attr" select="substring-before(concat($prioritized-attributes, ' '), ' ')"/>
            <xsl:apply-templates select="@*[name() = $current-attr]"/>
            <xsl:call-template name="apply-prioritized-attributes">
                <xsl:with-param name="prioritized-attributes" select="substring-after($prioritized-attributes, concat($current-attr, ' '))"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>

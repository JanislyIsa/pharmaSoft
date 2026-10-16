package pe.edu.pe.PharmaBackend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;
import pe.edu.pe.PharmaBackend.security.JwtAuthenticationFilter;
import pe.edu.pe.PharmaBackend.security.JwtService;
import pe.edu.pe.PharmaBackend.security.RestAccessDeniedHandler;
import pe.edu.pe.PharmaBackend.security.RestAuthenticationEntryPoint;

import static pe.edu.pe.PharmaBackend.enums.Permiso.CATALOGO_ESCRIBIR;
import static pe.edu.pe.PharmaBackend.enums.Permiso.CATALOGO_LEER;
import static pe.edu.pe.PharmaBackend.enums.Permiso.CLIENTES_ESCRIBIR;
import static pe.edu.pe.PharmaBackend.enums.Permiso.CLIENTES_LEER;
import static pe.edu.pe.PharmaBackend.enums.Permiso.USUARIOS_ADMINISTRAR;
import static pe.edu.pe.PharmaBackend.enums.Permiso.VENTAS_LEER;
import static pe.edu.pe.PharmaBackend.enums.Permiso.VENTAS_REGISTRAR;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private static final String[] RUTAS_PUBLICAS = {
            "/api/v1/auth/login",
            "/api/health",
            "/swagger-ui.html",
            "/swagger-ui/**",
            "/v3/api-docs/**",
            "/error"
    };

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http,
            JwtService jwtService,
            UserDetailsService userDetailsService,
            CorsConfigurationSource corsConfigurationSource,
            RestAuthenticationEntryPoint authenticationEntryPoint,
            RestAccessDeniedHandler accessDeniedHandler) throws Exception {

        JwtAuthenticationFilter jwtFilter = new JwtAuthenticationFilter(jwtService, userDetailsService);

        http
                .csrf(AbstractHttpConfigurer::disable)
                .logout(AbstractHttpConfigurer::disable)
                .cors(cors -> cors.configurationSource(corsConfigurationSource))
                .sessionManagement(sesion ->
                        sesion.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        // Publicas
                        .requestMatchers(RUTAS_PUBLICAS).permitAll()
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()

                        // Catalogo
                        .requestMatchers(HttpMethod.GET, "/api/v1/categorias/**", "/api/v1/productos/**")
                        .hasAuthority(CATALOGO_LEER.name())
                        .requestMatchers("/api/v1/categorias/**", "/api/v1/productos/**")
                        .hasAuthority(CATALOGO_ESCRIBIR.name())

                        // Clientes
                        .requestMatchers(HttpMethod.GET, "/api/v1/clientes/**")
                        .hasAuthority(CLIENTES_LEER.name())
                        .requestMatchers("/api/v1/clientes/**")
                        .hasAuthority(CLIENTES_ESCRIBIR.name())

                        // Ventas
                        .requestMatchers(HttpMethod.POST, "/api/v1/ventas")
                        .hasAuthority(VENTAS_REGISTRAR.name())
                        .requestMatchers(HttpMethod.GET, "/api/v1/ventas/**")
                        .hasAuthority(VENTAS_LEER.name())
                        .requestMatchers("/api/v1/ventas/**")
                        .hasAuthority(VENTAS_REGISTRAR.name())

                        // Administracion de la seguridad
                        .requestMatchers("/api/v1/usuarios/**", "/api/v1/empleados/**", "/api/v1/roles/**")
                        .hasAuthority(USUARIOS_ADMINISTRAR.name())

                        // Todo lo demas
                        .anyRequest().authenticated())
                .exceptionHandling(errores -> errores
                        .authenticationEntryPoint(authenticationEntryPoint)
                        .accessDeniedHandler(accessDeniedHandler))
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }
}